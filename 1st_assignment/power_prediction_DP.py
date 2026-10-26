"""
Predict pre-drilling and drilling cutting power, including tool entry and pilot bottom.

Author: Paolo Rossi
Co-author: GPT (GPT-6)
Date: 2026-10-26

The feed parameters describe total axial advance per revolution. Cutting forces
are sums of tangential force magnitudes over all lips; torque integrates their
radial arms. Lengths are final drill-tip depths measured from the original face.
Chisel-edge effects, withdrawal, spindle losses, and tool-change dynamics are
excluded. The lag runs from pre-drilling stop to first drilling material contact.
"""

# %% Imports and output settings
from pathlib import Path
import csv
import os
import sys

# Scripts start from their location; interactive cells use the working directory.
_settings_start = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
for _settings_root in (_settings_start, *_settings_start.parents):
    if (_settings_root / 'repo_settings.py').is_file():
        if str(_settings_root) not in sys.path:
            sys.path.insert(0, str(_settings_root))
        break
else:
    raise FileNotFoundError(
        "Cannot find repo_settings.py. Run interactive cells from within the repository."
    )

from repo_settings import configure_plots, output_dir, save_figure

configure_plots(headless=True)
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent if '__file__' in globals() else _settings_root / '1st_assignment'
OUTPUT_DIR = output_dir(SCRIPT_DIR)


# %% Turning reference: D = 24 mm at N = 1200 rpm
# Transfer the measured Kc and cutting speed, not the turning spindle speed.
D_reference = 24  # mm
N_reference = 1200  # rpm
turning_parameters = np.genfromtxt(
    OUTPUT_DIR / 'prediction_parameters_constant_n.csv', delimiter=',', names=True,
)
kc_parameters = np.genfromtxt(
    OUTPUT_DIR / 'kc_constant_n.csv', delimiter=',', names=True,
)
reference_rows = np.atleast_1d(turning_parameters)[
    np.isclose(np.atleast_1d(turning_parameters)['diameter_mm'], D_reference)
    & np.isclose(np.atleast_1d(turning_parameters)['spindle_speed_rpm'], N_reference)
]
kc_rows = np.atleast_1d(kc_parameters)[
    np.isclose(np.atleast_1d(kc_parameters)['diameter'], D_reference)
]
if len(reference_rows) != 1 or len(kc_rows) != 1:
    raise ValueError('Expected one 24 mm turning reference at 1200 rpm and one matching Kc row.')
Kc = float(kc_rows['Kc'][0])  # N/mm²
vc = float(reference_rows['cutting_speed_m_per_min'][0])  # m/min
if not np.isfinite(Kc) or Kc <= 0 or not np.isfinite(vc) or vc <= 0:
    raise ValueError('Reference Kc and cutting speed must be finite and positive.')


# %% Process parameters from README.md
D_pre = 5  # mm
point_angle_pre = 120  # degrees, included point angle
L_pre = 10  # mm, final pre-drilling tip depth
f_pre = 0.2  # mm/rev, total axial feed

D_drill = 13  # mm
D_pilot = D_pre  # mm, existing blind pilot hole
point_angle_drill = 120  # degrees, included point angle
L_drill = 20  # mm, final drilling tip depth
f_drill = 0.2  # mm/rev, total axial feed


# %% Pre-drilling: force, torque, and rotational cutting power
# The force is uniform per unit engaged radius: effective arm = r / 2.
# During entry both the force and arm increase, giving a quadratic power ramp.
# Pre-drilling kinematics: f_pre already includes all cutting lips.
alpha_pre = np.deg2rad(90 - point_angle_pre / 2)
R_pre = D_pre / 2  # mm
N_pre = vc * 1000 / (np.pi * D_pre)  # rpm, derived from the existing vc
# N_reference = 1200 rpm describes the turning reference, not the 5 mm drill.
Vf_pre = N_pre * f_pre  # mm/min; do not multiply by tooth count
omega_pre = 2 * np.pi * N_pre / 60  # rad/s
point_height_pre = R_pre * np.tan(alpha_pre)  # mm

t0_pre = 0.1  # s, first contact after display padding
t1_pre = t0_pre + point_height_pre / (Vf_pre / 60)  # full engagement
cutting_duration_pre = L_pre / (Vf_pre / 60)  # s, tip travel only
t_end_pre = t0_pre + cutting_duration_pre
dt_pre = 1 / (5 * N_pre / 60)  # s, same sampling rule as the exercise

# Include the exact contact, full-engagement (if reached), and stopping times.
t_active_pre = np.unique(np.r_[
    np.arange(t0_pre, t_end_pre, dt_pre),
    t0_pre, min(t1_pre, t_end_pre), t_end_pre,
])
z_active_pre = np.clip((t_active_pre - t0_pre) * Vf_pre / 60, 0, L_pre)
r_active_pre = np.minimum(z_active_pre / np.tan(alpha_pre), R_pre)

# Duplicate t_end_pre to show an instantaneous drop to zero at stopping.
t_pre = np.r_[0.0, t_active_pre, t_end_pre, t_end_pre + 0.1]
r_pre = np.r_[0.0, r_active_pre, 0.0, 0.0]
Fc_pre = np.abs(Kc * f_pre * r_pre)  # N, sum of magnitudes over all lips
Mc_pre = Fc_pre * (r_pre / 2) / 1000  # N·m, overall cutting torque
Pc_pre = Mc_pre * omega_pre  # W, overall rotational cutting power

print(f"Spindle speed: {N_pre:.1f} rpm; axial feed speed: {Vf_pre:.1f} mm/min")
print(f"Cutting time: {cutting_duration_pre:.4f} s; entry time: {t1_pre - t0_pre:.4f} s")
print(f"Maximum total cutting-force magnitude: {Fc_pre.max():.2f} N")
print(f"Maximum overall cutting power: {Pc_pre.max() / 1000:.3f} kW")


# %% Drilling: enlarge the blind pilot, then cut below its conical bottom
# Drilling kinematics and timing, using the parameters already defined above.
lag_drill = 0.5  # s, between the cutting phases
alpha_drill = np.deg2rad(90 - point_angle_drill / 2)
R_drill = D_drill / 2  # mm
R_pilot = D_pilot / 2  # mm
N_drill = vc * 1000 / (np.pi * D_drill)  # rpm
Vf_drill = N_drill * f_drill  # mm/min, total axial feed
omega_drill = 2 * np.pi * N_drill / 60  # rad/s
dt_drill = 1 / (5 * N_drill / 60)  # s

slope_drill = np.tan(alpha_drill)
slope_pre = np.tan(alpha_pre)
# First material contact lies on the pilot wall or bottom.
z_contact_drill = min(
    R_pilot * slope_drill,
    L_pre + min(0.0, (slope_drill - slope_pre) * R_pilot),
)
t0_drill = t_end_pre + lag_drill
t1_drill = t0_drill + (R_drill * slope_drill - z_contact_drill) / (Vf_drill / 60)
t_pilot_tip_drill = t0_drill + (L_pre - z_contact_drill) / (Vf_drill / 60)
t_end_drill = t0_drill + (L_drill - z_contact_drill) / (Vf_drill / 60)

# Entry and pilot-bottom events are sampled exactly.
z_events_drill = np.array([
    z_contact_drill, R_drill * slope_drill, L_pre,
    L_pre + (slope_drill - slope_pre) * R_pilot, L_drill,
])
z_events_drill = z_events_drill[
    (z_events_drill >= z_contact_drill) & (z_events_drill <= L_drill)
]
t_events_drill = t0_drill + (z_events_drill - z_contact_drill) / (Vf_drill / 60)
t_active_drill = np.unique(np.r_[
    np.arange(t0_drill, t_end_drill, dt_drill), t_events_drill,
])
# Sample either side of cavity transitions to display discontinuities faithfully.
t_transitions_drill = t0_drill + (
    np.array([L_pre, L_pre + (slope_drill - slope_pre) * R_pilot])
    - z_contact_drill
) / (Vf_drill / 60)
t_before_drill = np.nextafter(t_transitions_drill, -np.inf)
t_active_drill = np.unique(np.r_[
    t_active_drill,
    t_before_drill[(t_before_drill > t0_drill) & (t_before_drill < t_end_drill)],
    t_end_drill,
])
z_active_drill = z_contact_drill + (t_active_drill - t0_drill) * Vf_drill / 60

Fc_active_drill = []
Mc_active_drill = []
for z in z_active_drill:
    r_outer = min(z / slope_drill, R_drill)
    # The outer lips enlarge material outside the pilot diameter.
    radial_width = max(r_outer - R_pilot, 0.0)
    radial_moment = max(r_outer**2 - R_pilot**2, 0.0)

    # Equal 120-degree point angles make the inner lips engage simultaneously:
    # the pilot-bottom transition is a step, not an omitted entry ramp.
    # Inside the pilot diameter, cut only below its conical bottom:
    # z >= L_pre + rho * (slope_drill - slope_pre).
    inner_limit = min(R_pilot, r_outer)
    delta_slope = slope_drill - slope_pre
    if np.isclose(delta_slope, 0.0):
        inner_low, inner_high = (0.0, inner_limit) if z >= L_pre else (0.0, 0.0)
    elif delta_slope > 0:
        inner_low = 0.0
        inner_high = np.clip((z - L_pre) / delta_slope, 0, inner_limit)
    else:
        inner_low = np.clip((z - L_pre) / delta_slope, 0, inner_limit)
        inner_high = inner_limit
    radial_width += inner_high - inner_low
    radial_moment += inner_high**2 - inner_low**2

    Fc_active_drill.append(Kc * f_drill * radial_width)  # N, all lips
    Mc_active_drill.append(Kc * f_drill * radial_moment / 2000)  # N·m

Fc_active_drill = np.asarray(Fc_active_drill)
Mc_active_drill = np.asarray(Mc_active_drill)
Pc_active_drill = Mc_active_drill * omega_drill  # W, overall cutting power

t_drill = np.r_[t0_drill, t_active_drill, t_end_drill, t_end_drill + 0.1]
Fc_drill = np.r_[0.0, Fc_active_drill, 0.0, 0.0]
Mc_drill = np.r_[0.0, Mc_active_drill, 0.0, 0.0]
Pc_drill = np.r_[0.0, Pc_active_drill, 0.0, 0.0]

# One continuous timeline: pre-drilling, lag_drill at zero power, drilling.
t_total = np.r_[t_pre[:-1], t_drill]
Pc_total = np.r_[Pc_pre[:-1], Pc_drill]
print(f"Drilling speed: {N_drill:.1f} rpm; axial feed speed: {Vf_drill:.1f} mm/min")
print(f"First drilling contact: {t0_drill:.4f} s (lag: {lag_drill:.1f} s)")
print(f"Pilot-bottom transition: {t_pilot_tip_drill:.4f} s; stop: {t_end_drill:.4f} s")
print(f"Maximum drilling cutting power: {Pc_drill.max() / 1000:.3f} kW")


# %% Save one parameter row per phase, with units in the column names
parameters_csv_path = OUTPUT_DIR / 'pre_drilling_drilling_parameters.csv'
parameters_rows = []
for phase, diameter, pilot_diameter, pilot_depth, point_angle, tip_depth, feed, spindle_speed, feed_speed, lag, start, full_engagement, stop, force, torque, power in [
    ("pre_drilling", D_pre, 0.0, 0.0, point_angle_pre, L_pre, f_pre,
     N_pre, Vf_pre, 0.0, t0_pre, t1_pre, t_end_pre, Fc_pre, Mc_pre, Pc_pre),
    ("drilling", D_drill, D_pilot, L_pre, point_angle_drill, L_drill, f_drill,
     N_drill, Vf_drill, lag_drill, t0_drill, t1_drill, t_end_drill,
     Fc_drill, Mc_drill, Pc_drill),
]:
    parameters_rows.append({
        "phase": phase,
        "diameter_mm": diameter,
        "pilot_diameter_mm": pilot_diameter,
        "pilot_tip_depth_mm": pilot_depth,
        "point_angle_deg": point_angle,
        "final_tip_depth_mm": tip_depth,
        "feed_mm_per_rev": feed,
        "Kc_N_per_mm2": Kc,
        "cutting_speed_m_per_min": vc,
        "spindle_speed_rpm": spindle_speed,
        "feed_speed_mm_per_min": feed_speed,
        "lag_before_phase_s": lag,
        "start_time_s": start,
        "full_outer_engagement_time_s": full_engagement,
        "end_time_s": stop,
        "cutting_duration_s": stop - start,
        "max_cutting_force_magnitude_N": float(np.max(force)),
        "max_cutting_torque_Nm": float(np.max(torque)),
        "max_cutting_power_W": float(np.max(power)),
    })

with parameters_csv_path.open("w", newline="", encoding="utf-8") as parameters_file:
    parameters_writer = csv.DictWriter(parameters_file, fieldnames=list(parameters_rows[0]))
    parameters_writer.writeheader()
    parameters_writer.writerows(parameters_rows)

print(f'Saved: {os.path.relpath(parameters_csv_path, Path.cwd())}')


# %% Plot both phases in kW with the shared figure size and export settings
fig_power, ax_power = plt.subplots()
ax_power.plot(t_total, Pc_total / 1000, color='0.55', linewidth=1)
ax_power.plot(t_pre[:-1], Pc_pre[:-1] / 1000, color='tab:purple', linewidth=2,
              label=f'Pre-drilling: {D_pre:g} mm, {N_pre:.0f} rpm')
ax_power.plot(t_drill, Pc_drill / 1000, color='tab:blue', linewidth=2,
              label=f'Drilling: {D_drill:g} mm, {N_drill:.0f} rpm')
ax_power.axvspan(t_end_pre, t0_drill, color='0.92', label=f'Lag: {lag_drill:g} s')
if t0_pre < t1_pre <= t_end_pre:
    ax_power.axvline(t1_pre, color='tab:purple', linestyle=':', linewidth=1.5,
                     label='Pre-drilling: full engagement')
if t0_drill < t1_drill <= t_end_drill:
    ax_power.axvline(t1_drill, color='tab:blue', linestyle=':', linewidth=1.5,
                     label='Drilling: full outer-edge engagement')
if t0_drill < t_pilot_tip_drill < t_end_drill:
    ax_power.axvline(t_pilot_tip_drill, color='tab:orange', linestyle='--',
                     label='Inner lips engage below pilot bottom')
ax_power.set_xlabel('Time (s)')
ax_power.set_ylabel('Cutting power (kW)')
ax_power.set_title('Predicted Pre-drilling and Drilling Cutting Power')
ax_power.set_xlim(0, t_total[-1])
ax_power.set_ylim(bottom=0)
ax_power.grid(True, alpha=0.25)
ax_power.legend(loc='upper left', fontsize=9)
fig_power.tight_layout()
output_path = OUTPUT_DIR / 'prediction_power_vs_time_drilling.png'
save_figure(fig_power, output_path)
plt.close(fig_power)
print(f'Saved: {os.path.relpath(output_path, Path.cwd())}')
