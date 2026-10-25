"""Compare experimental and predicted cutting power at constant Vc and N.

Port of local_scratch/power_comparison.ipynb. Comparisons and pass averages
use raw power without moving-average filtering. Prediction amplitudes come
from the prediction CSVs, while aligned pass times come from the experiment.
Run power_prediction_TP.py first to generate the prediction CSVs.
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
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent if '__file__' in globals() else _settings_root / '1st_assignment'
OUTPUT_DIR = output_dir(SCRIPT_DIR)
DATA_DIR = SCRIPT_DIR / 'data'

# Notebook parameters. The median is used only to detect N cutting intervals.
CUTTING_THRESHOLD_W = 500
MIN_CUTTING_DURATION_S = 2.0
DETECTION_DURATION_S = {'vc': 0.0, 'n': 0.10}
BLUE = '#1f77b4'
ORANGE = '#ff7f0e'


# %% Load the first two columns and subtract non-cutting power by timestamp
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
    # Series subtraction and concat retain the union of timestamps and NaNs.
    df_exp = pd.concat([
        (cutting_vc - idle_vc).rename('power_vc'),
        (cutting_n - idle_n).rename('power_n'),
    ], axis=1).sort_index().reset_index()
    Ts = float(cutting_vc.index[1] - cutting_vc.index[0])
    if Ts <= 0 or not np.allclose(np.diff(df_exp['time']), Ts):
        raise ValueError('Pass detection requires a constant, increasing sampling interval.')
    return df_exp, Ts


# %% Detect and align cutting passes, then average raw power per diameter
def compare_power(df_exp, Ts, mode):
    column = f'power_{mode}'
    prediction_path = OUTPUT_DIR / f'prediction_parameters_constant_{mode}.csv'
    df_pred = pd.read_csv(prediction_path)
    signal = df_exp[column]

    # A brief median window prevents dips from splitting the final N pass.
    # With duration=0 the Vc detector uses raw power, as in the notebook.
    detection_samples = max(1, round(DETECTION_DURATION_S[mode] / Ts))
    if detection_samples % 2 == 0:
        detection_samples += 1
    detection = signal.rolling(
        detection_samples, center=True, min_periods=1
    ).median()
    cutting = ((detection > CUTTING_THRESHOLD_W) & signal.notna()).to_numpy()
    edges = np.diff(np.r_[False, cutting, False].astype(int))
    starts = np.flatnonzero(edges == 1)
    stops = np.flatnonzero(edges == -1)  # Exclusive.
    keep = (stops - starts) * Ts >= MIN_CUTTING_DURATION_S
    starts, stops = starts[keep], stops[keep]
    if len(starts) != len(df_pred):
        raise ValueError(
            f'{mode}: detected {len(starts)} cutting intervals for {len(df_pred)} '
            'predicted passes. Review CUTTING_THRESHOLD_W, MIN_CUTTING_DURATION_S '
            'and DETECTION_DURATION_S.'
        )

    # Keep CSV timing intact: measured intervals replace it only for alignment.
    aligned = df_pred.copy()
    aligned['aligned_start_s'] = df_exp['time'].iloc[starts].to_numpy()
    aligned['aligned_end_s'] = df_exp['time'].iloc[stops - 1].to_numpy() + Ts
    comparison = df_exp[['time', column]].copy()
    predicted_column = f'{column}_predicted'
    comparison[predicted_column] = 0.0
    for start, stop, power in zip(starts, stops, df_pred['cutting_power_W']):
        comparison.iloc[start:stop, comparison.columns.get_loc(predicted_column)] = power
    comparison.loc[signal.isna(), predicted_column] = np.nan

    # Equally spaced samples have equal weight. Missing samples are excluded;
    # no detection smoothing is applied to the values being averaged.
    summary = pd.DataFrame({
        'diameter_mm': df_pred['diameter_mm'].to_numpy(),
        'predicted_power_W': df_pred['cutting_power_W'].to_numpy(),
        'avg_experimental_power_W': [
            signal.iloc[start:stop].mean() for start, stop in zip(starts, stops)
        ],
    })
    predicted = summary['predicted_power_W']
    summary['percentage_deviation_pct'] = 100 * (
        summary['avg_experimental_power_W'] - predicted
    ) / predicted.replace(0, np.nan)
    return comparison, aligned, summary


# %% Export static figures with repository settings
def report_saved(path):
    print(f'Saved: {os.path.relpath(path, Path.cwd())}')


def export_plot(time, curves, filename, title, boundaries=()):
    """curves: (power in W, label, color, width, step) tuples."""
    fig, ax = plt.subplots()
    for values, label, color, width, step in curves:
        # Convert only the plotted values; calculations and CSVs remain in W.
        ax.plot(time, np.asarray(values) / 1000, label=label, color=color, linewidth=width,
                drawstyle='steps-post' if step else 'default')
    for boundary in boundaries:
        ax.axvline(boundary, color='lightgray', linestyle='--', linewidth=1, zorder=0)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Power (kW)')
    ax.set_title(title)
    if len(curves) > 1:
        ax.legend()
    ax.grid(True)
    fig.tight_layout()
    png_path = OUTPUT_DIR / f'{filename}.png'
    save_figure(fig, png_path)
    plt.close(fig)
    report_saved(png_path)


# %% Run both operating modes
def main():
    df_exp, Ts = load_experimental_power()
    for mode, label in [('vc', 'Vc constant'), ('n', 'N constant')]:
        column = f'power_{mode}'
        comparison, aligned, summary = compare_power(df_exp, Ts, mode)

        csv_path = OUTPUT_DIR / f'power_comparison_constant_{mode}.csv'
        summary.to_csv(csv_path, index=False, na_rep='NaN')
        print(f'\n{label}: {len(summary)} passes; sampling interval {Ts:g} s')
        print(summary.to_string(index=False, float_format=lambda value: f'{value:.2f}'))
        report_saved(csv_path)

        operating_mode = 'Constant Cutting Velocity' if mode == 'vc' else 'Constant Spindle Speed'
        export_plot(df_exp['time'], [
            (df_exp[column], 'Experimental', BLUE, 1, False),
        ], f'experimental_power_constant_{mode}',
            f'Experimental Cutting Power\n{operating_mode}')
        export_plot(comparison['time'], [
            (comparison[column], 'Experimental', BLUE, 2, False),
            (comparison[f'{column}_predicted'], 'Predicted', ORANGE, 2, True),
        ], f'power_comparison_constant_{mode}',
            f'Cutting Power: Experimental vs. Predicted\n{operating_mode}',
            aligned['aligned_start_s'].iloc[1:])


if __name__ == '__main__':
    main()
