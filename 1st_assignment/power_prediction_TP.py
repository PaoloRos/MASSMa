"""
Predict cutting power versus time

Author: Paolo Rossi
Co-author: GPT (GPT-6)
Date: 2026-10-25
"""

# %% Imports and output settings
from pathlib import Path
import os

import numpy as np
import matplotlib

# Use a non-interactive backend: save figures without opening plot windows.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Use the script location normally. Interactive cells may not define __file__;
# in that case, run from the project root or from 1st_assignment.
if '__file__' in globals():
    SCRIPT_DIR = Path(__file__).resolve().parent
else:
    SCRIPT_DIR = Path.cwd()
    if (SCRIPT_DIR / '1st_assignment').is_dir():
        SCRIPT_DIR = SCRIPT_DIR / '1st_assignment'
OUTPUT_DIR = SCRIPT_DIR / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Golden ratio applies to the whole figure canvas: width / height = phi.
# Do not use bbox_inches='tight' when saving: it would change that ratio.
GOLDEN_RATIO = (1 + np.sqrt(5)) / 2
FIGURE_WIDTH = 10  # inches
FIGURE_SIZE = (FIGURE_WIDTH, FIGURE_WIDTH / GOLDEN_RATIO)
OUTPUT_DPI = 200


# %%
# Workpiece parameters
L = 40            # mm, axial cutting length of one forward pass
Ds = 46           # mm, diameter machined by the first pass (initial stock: 48 mm)
De = 24           # mm, diameter machined by the final pass

# Tool parameters
ap = 1            # mm, radial depth of cut; each pass reduces diameter by 2 * ap
f = 0.2           # mm/rev, axial feed per spindle revolution
Vc_const = 150    # m/min
Kc_vc = 3025.6    # MPa, specific cutting pressure at constant Vc
N_const = 1200    # rpm
Kc_n = 3230.3     # MPa, specific cutting pressure at constant N

# %%
# Evaluate one block at each diameter, including both Ds and De.
# Adjacent diameters differ by 2 * ap (the diametral depth of cut).
# The model assumes Ds - De is an integer multiple of 2 * ap.
D = np.arange(Ds, De - ap, -2 * ap)  # mm: 46, 44, ..., 24
D_passes = D.copy()
n = len(D_passes)  # 12 prediction blocks, including the 24 mm block

# --- Power prediction ---

# Cutting force = specific cutting pressure * uncut chip area (ap * f).
# Power = force * cutting speed; divide m/min by 60 to obtain m/s.
# At constant Vc, the predicted power is identical in all n blocks.
# Vc constant
Fc_vc = Kc_vc * ap * f                   # N
Pc_vc = np.full(n, Fc_vc * Vc_const / 60)   # W

# At constant spindle speed, Vc = pi * D * N / 1000 (mm to metres).
# As the machined diameter decreases, cutting speed and power decrease.
# Power for N constant
Vc = np.pi * D_passes * N_const / 1000              # m/min
Fc_n = Kc_n * ap * f                          # N
Pc_n = Fc_n * Vc / 60                          # W

# %%
# --- Timing prediction ---

# Feed speed is f * N in mm/min. Only the forward stroke cuts over length L.
# The tool retracts and returns rapidly: that stroke is not another L at Vf.
# Cutting time is L / Vf (minutes), multiplied by 60 to obtain seconds.
# Return, approach and positioning times are excluded from this prediction.
# At constant Vc, N increases as diameter decreases, shortening cutting times.
N_vc = Vc_const * 1000 / (np.pi * D_passes)  # rpm
Vf_vc = f * N_vc                             # mm/min
t_vc = L / Vf_vc * 60                       # s, cutting time per pass

# At constant N, the feed speed and all block durations are identical.
Vf_n = f * N_const                             # mm/min
t_n = np.full(n, L / Vf_n * 60)             # s, 10 s per cutting pass

# %%
# Save one row per predicted block, separately for the two operating modes.
# time_s and time_end_s are cumulative cutting times, not machine-cycle times;
# duration_s is the cutting duration of that pass. Non-cutting gaps are omitted.
# All remaining parameters apply over that entire interval. Each listed
# diameter, including De, has its own row and plotted step, covering length L.
time_edges_vc = np.concatenate(([0], np.cumsum(t_vc)))
time_edges_n = np.concatenate(([0], np.cumsum(t_n)))

csv_header = (
    'time_s,time_end_s,duration_s,diameter_mm,cutting_speed_m_per_min,'
    'spindle_speed_rpm,feed_speed_mm_per_min,cutting_power_W'
)

# Constant cutting speed: spindle speed, feed speed and duration vary.
parameters_vc = np.column_stack((
    time_edges_vc[:-1], time_edges_vc[1:], t_vc, D_passes,
    np.full(n, Vc_const), N_vc, Vf_vc, Pc_vc,
))
output_path = OUTPUT_DIR / 'prediction_parameters_constant_vc.csv'
# Suppress NumPy's default '#' header prefix for a standard CSV header.
np.savetxt(output_path, parameters_vc, delimiter=',', header=csv_header,
           comments='', fmt='%.10g')
print(f'Saved: {os.path.relpath(output_path, Path.cwd())}')

# Constant spindle speed: cutting speed and power vary with diameter.
parameters_n = np.column_stack((
    time_edges_n[:-1], time_edges_n[1:], t_n, D_passes,
    Vc, np.full(n, N_const), np.full(n, Vf_n), Pc_n,
))
output_path = OUTPUT_DIR / 'prediction_parameters_constant_n.csv'
np.savetxt(output_path, parameters_n, delimiter=',', header=csv_header,
           comments='', fmt='%.10g')
print(f'Saved: {os.path.relpath(output_path, Path.cwd())}')

# %%
# Power vs time: Vc constant

fig, ax = plt.subplots(figsize=FIGURE_SIZE)
# Draw each power value over its own time interval.
ax.stairs(Pc_vc, time_edges_vc, baseline=None, color='#2166ac', linewidth=2)
# Dashed vertical lines mark internal block boundaries.
for boundary in time_edges_vc[1:-1]:
    ax.axvline(boundary, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
ax.set_xlabel('Cumulative cutting time (s)')
ax.set_ylabel('Power (W)')
ax.set_title('Predicted Cutting Power — Constant Cutting Speed')
ax.set_xlim(0, time_edges_vc[-1])
# Tight y-axis limits, with padding even when power is constant.
y_min = Pc_vc.min()
y_max = Pc_vc.max()
y_padding = max(0.05 * (y_max - y_min), 0.02 * abs(y_max), 1.0)
ax.set_ylim(y_min - y_padding, y_max + y_padding)
ax.grid(axis='y', alpha=0.25)
fig.tight_layout()
# Save the full canvas to preserve the golden ratio (up to pixel rounding).
output_path = OUTPUT_DIR / 'prediction_power_vs_time_constant_vc.png'
fig.savefig(output_path, dpi=OUTPUT_DPI, facecolor='white', bbox_inches=None)
plt.close(fig)
# Relative paths avoid spaces in the project location and are clickable in VS Code.
# Cmd-click the path in the integrated terminal to open the PNG preview.
print(f'Saved: {os.path.relpath(output_path, Path.cwd())}')

# %%
# Power vs time: N constant

fig, ax = plt.subplots(figsize=FIGURE_SIZE)
# Draw each power value over its own time interval.
ax.stairs(Pc_n, time_edges_n, baseline=None, color='#b35806', linewidth=2)
# Dashed vertical lines mark internal block boundaries.
for boundary in time_edges_n[1:-1]:
    ax.axvline(boundary, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
ax.set_xlabel('Cumulative cutting time (s)')
ax.set_ylabel('Power (W)')
ax.set_title('Predicted Cutting Power — Constant Spindle Speed')
ax.set_xlim(0, time_edges_n[-1])
# Tight y-axis limits, with padding even when power is constant.
y_min = Pc_n.min()
y_max = Pc_n.max()
y_padding = max(0.05 * (y_max - y_min), 0.02 * abs(y_max), 1.0)
ax.set_ylim(y_min - y_padding, y_max + y_padding)
ax.grid(axis='y', alpha=0.25)
fig.tight_layout()
# Save the full canvas to preserve the golden ratio (up to pixel rounding).
output_path = OUTPUT_DIR / 'prediction_power_vs_time_constant_n.png'
fig.savefig(output_path, dpi=OUTPUT_DPI, facecolor='white', bbox_inches=None)
plt.close(fig)
# Relative paths avoid spaces in the project location and are clickable in VS Code.
# Cmd-click the path in the integrated terminal to open the PNG preview.
print(f'Saved: {os.path.relpath(output_path, Path.cwd())}')
