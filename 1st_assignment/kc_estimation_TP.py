"""
Estimate specific cutting pressure at constant cutting speed and spindle speed.

Author: Paolo Rossi
Co-author: GPT (GPT-6)
Date: 2026-10-25

Port of local_scratch/kc_prediction_TP.ipynb. Export per-diameter mean Kc CSVs
and only the two power plots showing the windows retained for calculation.
Constant Vc uses a centered moving average; constant N uses raw power.
The median is used only for detection and is never plotted.
Run power_prediction_TP.py first to generate the parameter CSVs.
"""

# %% Imports and shared output settings
from pathlib import Path
import os
import sys

_settings_start = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
for _settings_root in (_settings_start, *_settings_start.parents):
    if (_settings_root / 'repo_settings.py').is_file():
        if str(_settings_root) not in sys.path:
            sys.path.insert(0, str(_settings_root))
        break
else:
    raise FileNotFoundError(
        'Cannot find repo_settings.py. Run interactive cells from within the repository.'
    )

from repo_settings import configure_plots, output_dir, save_figure

configure_plots(headless=True)
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent if '__file__' in globals() else _settings_root / '1st_assignment'
OUTPUT_DIR = output_dir(SCRIPT_DIR)
DATA_DIR = SCRIPT_DIR / 'data'

FEED_MM_PER_REV = 0.2
DEPTH_OF_CUT_MM = 1.0
CUTTING_THRESHOLD_W = {'vc': 1000.0, 'n': 500.0}
DETECTION_DURATION_S = {'vc': 0.20, 'n': 0.10}
MOVING_AVERAGE_SAMPLES = {'vc': 55, 'n': 1}
MIN_CUTTING_DURATION_S = 2.0
BLUE = '#1f77b4'
ORANGE = '#d97706'


# %% Load experimental power and subtract idle power by timestamp
def load_experimental_power():
    def read_power(filename, skiprows):
        frame = pd.read_csv(DATA_DIR / filename, skiprows=skiprows, usecols=[0, 1])
        frame.columns = ['time', 'power']
        if not frame['time'].is_unique:
            raise ValueError(f'Duplicate timestamps in {filename}.')
        return frame.set_index('time')['power']

    cutting_vc = read_power('ANNACHPTVC150.csv', 8)
    idle_vc = read_power('ANNACHPTVC150VIDE.csv', 9)
    cutting_n = read_power('ANNACHPT1200RPM.csv', 9)
    idle_n = read_power('ANNACHPT1200RPMVIDE.csv', 9)
    df_exp = pd.concat([
        (cutting_vc - idle_vc).rename('power_vc'),
        (cutting_n - idle_n).rename('power_n'),
    ], axis=1).sort_index().reset_index()
    Ts = float(cutting_vc.index[1] - cutting_vc.index[0])
    if Ts <= 0 or not np.allclose(np.diff(df_exp['time']), Ts):
        raise ValueError('Pass detection requires a constant, increasing sampling interval.')
    return df_exp, Ts


# %% Select windows, calculate sample Kc, and summarize each diameter
def estimate_kc(df_exp, Ts, mode):
    prediction = pd.read_csv(OUTPUT_DIR / f'prediction_parameters_constant_{mode}.csv')
    required = ['duration_s', 'diameter_mm', 'cutting_speed_m_per_min']
    if (not np.isfinite(prediction[required]).all().all()
            or not prediction[required].gt(0).all().all()):
        raise ValueError(f'{mode}: CSV durations, diameters and speeds must be finite and positive.')
    if not (np.isfinite([FEED_MM_PER_REV, DEPTH_OF_CUT_MM]).all()
            and min(FEED_MM_PER_REV, DEPTH_OF_CUT_MM) > 0):
        raise ValueError('Feed and depth of cut must be finite and positive.')

    time = df_exp['time'].to_numpy(dtype=float)
    signal = df_exp[f'power_{mode}']
    detection_samples = max(1, round(DETECTION_DURATION_S[mode] / Ts))
    if detection_samples % 2 == 0:
        detection_samples += 1
    detection = signal.rolling(detection_samples, center=True, min_periods=1).median()
    cutting = ((detection > CUTTING_THRESHOLD_W[mode]) & signal.notna()).to_numpy()
    edges = np.diff(np.r_[False, cutting, False].astype(int))
    starts = np.flatnonzero(edges == 1)
    stops = np.flatnonzero(edges == -1)  # Exclusive.
    keep = (stops - starts) * Ts >= MIN_CUTTING_DURATION_S
    starts, stops = starts[keep], stops[keep]
    if len(starts) != len(prediction):
        raise ValueError(
            f'{mode}: detected {len(starts)} cutting intervals for {len(prediction)} CSV passes. '
            'Review CUTTING_THRESHOLD_W, DETECTION_DURATION_S and MIN_CUTTING_DURATION_S.'
        )

    window_samples = MOVING_AVERAGE_SAMPLES[mode]
    power = signal.rolling(window_samples, center=True, min_periods=window_samples).mean()
    left_samples = window_samples // 2
    right_samples = (window_samples - 1) // 2
    windows = prediction[required].copy()
    windows.insert(0, 'pass', np.arange(1, len(prediction) + 1))
    windows['start_s'] = time[starts]
    windows['end_s'] = windows['start_s'] + windows['duration_s']
    windows['measured_end_s'] = time[stops - 1] + Ts
    analysis_starts, analysis_ends, means, standard_deviations = [], [], [], []
    previous_stop = 0

    for row, start, detected_stop in zip(windows.itertuples(index=False), starts, stops):
        if mode == 'vc':
            # Keep every contributing moving-average sample inside the cut.
            first = start + left_samples
            stop = min(detected_stop, np.searchsorted(time, row.end_s, side='left')) - right_samples
            analysis_end = time[stop - 1] + Ts if stop > first else np.nan
        else:
            # Preserve the notebook's exact [start, min(CSV end, detected end)) mask.
            first = start
            analysis_end = min(row.end_s, row.measured_end_s)
            stop = np.searchsorted(time, analysis_end, side='left')
        if first >= stop or first < previous_stop:
            raise ValueError(f'{mode}, pass {row[0]}: retained window is empty or overlaps its predecessor.')
        previous_stop = stop
        kc = power.iloc[first:stop] * 60.0 / (
            row.cutting_speed_m_per_min * FEED_MM_PER_REV * DEPTH_OF_CUT_MM
        )
        if kc.count() < 2 or np.isinf(kc).any():
            raise ValueError(f'{mode}, pass {row[0]}: at least two finite Kc samples are required.')
        analysis_starts.append(time[first])
        analysis_ends.append(analysis_end)
        means.append(kc.mean())
        standard_deviations.append(kc.std(ddof=1))

    windows['analysis_start_s'] = analysis_starts
    windows['analysis_end_s'] = analysis_ends
    summary = pd.DataFrame({
        'diameter': prediction['diameter_mm'].to_numpy(),
        'Kc': means,
        'Kc_std': standard_deviations,
    })
    return power, windows, summary


# %% Export only the two selected-window plots, with power in kW
def report_saved(path):
    print(f'Saved: {os.path.relpath(path, Path.cwd())}')


def export_window_plot(df_exp, power, windows, mode):
    fig, ax = plt.subplots()
    # Only plotted power is converted to kW; calculations remain in W.
    valid = df_exp[f'power_{mode}'].notna()
    time = df_exp.loc[valid, 'time']
    if mode == 'vc':
        ax.plot(time, df_exp.loc[valid, 'power_vc'] / 1000,
                color='lightgray', linewidth=0.7, label='Raw cutting power')
        ax.plot(time, power.loc[valid] / 1000,
                color=BLUE, linewidth=1.5, label='Moving average')
    else:
        ax.plot(time, power.loc[valid] / 1000,
                color=BLUE, linewidth=0.7, label='Raw cutting power (used for Kc)')
    ax.axhline(CUTTING_THRESHOLD_W[mode] / 1000, color=ORANGE, linewidth=1,
               linestyle='--', label=f'Entry / exit threshold: {CUTTING_THRESHOLD_W[mode] / 1000:g} kW')
    for row in windows.itertuples(index=False):
        ax.axvspan(row.start_s, row.end_s, facecolor='none',
                   edgecolor=ORANGE, linewidth=0.8, linestyle='--', zorder=0)
        ax.axvspan(row.analysis_start_s, row.analysis_end_s,
                   color=BLUE, alpha=0.12, linewidth=0, zorder=0)
        ax.text((row.analysis_start_s + row.analysis_end_s) / 2, 0.98, str(row[0]),
                transform=ax.get_xaxis_transform(), ha='center', va='top', fontsize=9)
    handles, labels = ax.get_legend_handles_labels()
    handles.extend([
        Patch(facecolor='none', edgecolor=ORANGE, linestyle='--', label='Predicted window'),
        Patch(facecolor=BLUE, alpha=0.15, label='Retained for Kc (shaded)'),
    ])
    labels.extend(['Predicted window', 'Retained for Kc (shaded)'])
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.94),
               ncol=3, fontsize=9, frameon=False)
    title = 'Constant Cutting Speed' if mode == 'vc' else 'Constant Spindle Speed'
    fig.suptitle(title, y=0.99)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Cutting power (kW)')
    ax.grid(True, alpha=0.3)
    ax.margins(x=0.01)
    fig.tight_layout(rect=(0, 0, 1, 0.85))
    png_path = OUTPUT_DIR / f'kc_windows_constant_{mode}.png'
    save_figure(fig, png_path)
    plt.close(fig)
    report_saved(png_path)


# %% Generate report outputs for both operating modes
def main():
    df_exp, Ts = load_experimental_power()
    for mode, label in [('vc', 'Vc constant'), ('n', 'N constant')]:
        power, windows, summary = estimate_kc(df_exp, Ts, mode)
        csv_path = OUTPUT_DIR / f'kc_constant_{mode}.csv'
        summary[['diameter', 'Kc', 'Kc_std']].to_csv(csv_path, index=False)
        print(f'\n{label}: {len(summary)} passes; Kc and SD in N/mm²')
        print(summary.to_string(index=False, float_format=lambda value: f'{value:.2f}'))
        # Equal weight per pass; SD describes variability between pass means.
        print(f'Mean of pass means: {summary["Kc"].mean():.2f} N/mm²')
        print(f'Sample SD between pass means: {summary["Kc"].std(ddof=1):.2f} N/mm²')
        report_saved(csv_path)
        export_window_plot(df_exp, power, windows, mode)


if __name__ == '__main__':
    main()
