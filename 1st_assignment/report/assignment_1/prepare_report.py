"""Generate checked LaTeX tables from assignment CSVs and the existing detectors.

Run with the repository's Python environment after the four analysis scripts.
No experimental data or analysis outputs are modified here.
"""

from datetime import datetime
from pathlib import Path
import csv
import importlib.util
import json
import math
import shutil
import statistics
from zoneinfo import ZoneInfo

import numpy as np


PROJECT = Path(__file__).resolve().parent
ASSIGNMENT = PROJECT.parents[1]
OUTPUTS = ASSIGNMENT / "outputs"
GENERATED = PROJECT / "generated"


def load_module(filename):
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), ASSIGNMENT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(filename):
    with (OUTPUTS / filename).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return [
        {key: value if key == "phase" else float(value) for key, value in row.items()}
        for row in rows
    ]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_rows(filename, rows):
    commands = {
        "prediction_rows.tex": "PredictionRows", "timing_rows.tex": "TimingRows",
        "power_vc_rows.tex": "PowerVcRows", "power_n_rows.tex": "PowerNRows",
        "kc_rows.tex": "KcRows", "drilling_rows.tex": "DrillingRows",
    }
    (GENERATED / filename).write_text(
        "\\newcommand{\\" + commands[filename] + "}{%\n" +
        "\n".join(" & ".join(row) + r" \\" for row in rows) + "\n}\n", encoding="utf-8"
    )


def main():
    GENERATED.mkdir(exist_ok=True)
    images = PROJECT / "images"
    images.mkdir(exist_ok=True)
    shutil.copy2(ASSIGNMENT.parent / "unitn_logo.png", images / "unitn_logo.png")
    for filename in ["power_comparison_constant_vc.png", "power_comparison_constant_n.png",
                     "kc_windows_constant_vc.png", "kc_windows_constant_n.png",
                     "prediction_power_vs_time_drilling.png"]:
        shutil.copy2(OUTPUTS / filename, images / filename)
    comparison = load_module("power_comparison_TP.py")
    estimation = load_module("kc_estimation_TP.py")
    experimental, sample_period = comparison.load_experimental_power()
    modes = {}
    timing_rows, prediction_rows = [], []
    macros = {}
    for mode, suffix, mode_tex in [("vc", "Vc", r"Constant $v_c$"), ("n", "N", r"Constant $N$")]:
        prediction = read_csv(f"prediction_parameters_constant_{mode}.csv")
        power = read_csv(f"power_comparison_constant_{mode}.csv")
        kc = read_csv(f"kc_constant_{mode}.csv")
        diameters = [row["diameter_mm"] for row in prediction]
        require(diameters == list(range(46, 23, -2)), f"{mode}: expected 12 ordered turning passes")
        require([row["diameter_mm"] for row in power] == diameters, f"{mode}: power pass pairing differs")
        require([row["diameter"] for row in kc] == diameters, f"{mode}: Kc pass pairing differs")
        require(all(math.isfinite(value) for rows in [prediction, power, kc] for row in rows for value in row.values()),
                f"{mode}: missing/non-finite report data")
        _, aligned, recomputed_power = comparison.compare_power(experimental, sample_period, mode)
        _, _, recomputed_kc = estimation.estimate_kc(experimental, sample_period, mode)
        for stored, recomputed in [(power, recomputed_power), (kc, recomputed_kc)]:
            for key in recomputed.columns:
                require(np.allclose([row[key] for row in stored], recomputed[key], rtol=1e-10, atol=1e-8),
                        f"{mode}: stale CSV column {key}; rerun the analysis scripts")
        nominal_kc = 3025.6 if mode == "vc" else 3230.3
        for row in prediction:
            expected_power = nominal_kc * row["cutting_speed_m_per_min"] * 0.2 / 60
            expected_duration = 60 * 40 / (0.2 * row["spindle_speed_rpm"])
            require(math.isclose(row["cutting_power_W"], expected_power, rel_tol=1e-9), "Prediction power changed")
            require(math.isclose(row["duration_s"], expected_duration, rel_tol=1e-9), "Prediction timing changed")
        detected_duration = aligned["aligned_end_s"] - aligned["aligned_start_s"]
        predicted_duration = aligned["duration_s"]
        predicted_total, detected_total = float(predicted_duration.sum()), float(detected_duration.sum())
        timing = {
            "predicted_total_s": predicted_total,
            "detected_total_s": detected_total,
            "signed_total_difference_pct": 100 * (detected_total - predicted_total) / predicted_total,
            "duration_mae_s": float((detected_duration - predicted_duration).abs().mean()),
            "predicted_pass_durations_s": predicted_duration.tolist(),
            "detected_pass_durations_s": detected_duration.tolist(),
        }
        timing_rows.append([mode_tex, f"{predicted_total:.2f}", f"{detected_total:.2f}",
                            f"{timing['signed_total_difference_pct']:+.2f}", f"{timing['duration_mae_s']:.3f}"])
        def endpoint_range(column, decimals):
            first, last = prediction[0][column], prediction[-1][column]
            if column == "cutting_power_W":
                first, last = first / 1000, last / 1000
            return f"{first:.{decimals}f}" if first == last else f"${first:.{decimals}f} \\to {last:.{decimals}f}$"
        prediction_rows.append([mode_tex, endpoint_range("cutting_speed_m_per_min", 2),
                                endpoint_range("spindle_speed_rpm", 0), endpoint_range("cutting_power_W", 3),
                                endpoint_range("duration_s", 2)])
        write_rows(f"power_{mode}_rows.tex", [
            [str(index), f"{row['diameter_mm']:.0f}", f"{row['predicted_power_W']/1000:.3f}",
             f"{row['avg_experimental_power_W']/1000:.3f}", f"{row['std_experimental_power_W']/1000:.3f}",
             f"{row['percentage_deviation_pct']:+.2f}"] for index, row in enumerate(power, 1)
        ])
        means = [row["Kc"] for row in kc]
        errors = [abs(row["percentage_deviation_pct"]) for row in power]
        macros.update({f"MeanKc{suffix}": f"{statistics.mean(means):.2f}",
                       f"BetweenSd{suffix}": f"{statistics.stdev(means):.2f}",
                       f"MaxError{suffix}": f"{max(errors):.2f}",
                       f"MinError{suffix}": f"{min(errors):.2f}",
                       f"MeanError{suffix}": f"{statistics.mean(errors):.2f}"})
        modes[mode] = {"prediction": prediction, "power": power, "kc": kc, "timing": timing}
    write_rows("timing_rows.tex", timing_rows)
    write_rows("prediction_rows.tex", prediction_rows)
    write_rows("kc_rows.tex", [
        [f"{a['diameter']:.0f}", f"{a['Kc']:.2f}", f"{a['Kc_std']:.2f}",
         f"{b['Kc']:.2f}", f"{b['Kc_std']:.2f}"]
        for a, b in zip(modes["vc"]["kc"], modes["n"]["kc"])
    ])

    drilling = read_csv("pre_drilling_drilling_parameters.csv")
    require([row["phase"] for row in drilling] == ["pre_drilling", "drilling"], "Unexpected drilling phases")
    reference_kc = modes["n"]["kc"][-1]["Kc"]
    reference_vc = modes["n"]["prediction"][-1]["cutting_speed_m_per_min"]
    for row, diameter, tip_depth in zip(drilling, [5, 13], [10, 20]):
        require(row["diameter_mm"] == diameter and row["final_tip_depth_mm"] == tip_depth,
                "Drilling geometry changed")
        require(row["point_angle_deg"] == 120 and row["feed_mm_per_rev"] == 0.2, "Drilling angle/feed changed")
        require(math.isclose(row["Kc_N_per_mm2"], reference_kc), "Drilling uses a different Kc reference")
        require(math.isclose(row["cutting_speed_m_per_min"], reference_vc), "Drilling speed transfer differs")
        require(math.isclose(row["spindle_speed_rpm"], reference_vc * 1000 / (math.pi * diameter)),
                "Drilling spindle speed is inconsistent")
        require(math.isclose(row["max_cutting_power_W"], reference_kc * 0.2 * diameter * reference_vc / 240),
                "Full-engagement drilling power is inconsistent with the formula sheet")
    require(drilling[1]["lag_before_phase_s"] == 0.5, "Illustrative drilling lag changed")
    write_rows("drilling_rows.tex", [
        [phase, f"{row['diameter_mm']:.0f}", f"{row['final_tip_depth_mm']:.0f}", r"$120^\circ$",
         f"{row['spindle_speed_rpm']:.0f}", f"{row['cutting_duration_s']:.3f}",
         f"{row['max_cutting_power_W']/1000:.3f}"]
        for phase, row in zip(["Pre-Drilling", "Drilling"], drilling)
    ])
    today = datetime.now(ZoneInfo("Europe/Rome"))
    macros.update({
        "ReportDate": f"{today.day} {today.strftime('%B %Y')}",
        "SamplePeriod": f"{sample_period:.3f}",
        "PredPowerVc": f"{modes['vc']['prediction'][0]['cutting_power_W']/1000:.3f}",
        "FirstMeanN": f"{modes['n']['power'][0]['avg_experimental_power_W']/1000:.3f}",
        "LastMeanN": f"{modes['n']['power'][-1]['avg_experimental_power_W']/1000:.3f}",
        "FirstKcN": f"{modes['n']['kc'][0]['Kc']:.2f}", "LastKcN": f"{reference_kc:.2f}",
        "ReferenceVc": f"{reference_vc:.2f}",
        "KcDifference": f"{100*(statistics.mean(row['Kc'] for row in modes['n']['kc']) / statistics.mean(row['Kc'] for row in modes['vc']['kc'])-1):.2f}",
        "PrePower": f"{drilling[0]['max_cutting_power_W']/1000:.3f}",
        "DrillPower": f"{drilling[1]['max_cutting_power_W']/1000:.3f}",
        "AnnularPower": f"{drilling[1]['max_cutting_power_W']/1000*(1-(5/13)**2):.3f}",
    })
    for mode, suffix in [("vc", "Vc"), ("n", "N")]:
        samples = max(1, round(estimation.DETECTION_DURATION_S[mode] / sample_period))
        samples += samples % 2 == 0
        macros[f"MedianSamples{suffix}"] = str(samples)
    (GENERATED / "results.tex").write_text(
        "% Generated by prepare_report.py; do not edit numeric values here.\n" +
        "\n".join(f"\\newcommand{{\\{key}}}{{{value}}}" for key, value in macros.items()) + "\n",
        encoding="utf-8",
    )
    with (GENERATED / "results.tex").open("a", encoding="utf-8") as stream:
        for filename in ["prediction_rows.tex", "timing_rows.tex", "power_vc_rows.tex",
                         "power_n_rows.tex", "kc_rows.tex", "drilling_rows.tex"]:
            stream.write(f"\\input{{generated/{filename}}}\n")
    audit = {"production_date": today.isoformat(), "sample_period_s": sample_period,
             "timing": {mode: data["timing"] for mode, data in modes.items()},
             "report_values": macros}
    (GENERATED / "evidence.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
