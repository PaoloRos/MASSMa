# 1st Assignment - Data Analysis from turning machining
# MASSMa Course
#
# Paolo Rossi, 235651, Università di Trento
# Trento 30/10/2025
#
#

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import numpy as np

DPI = 300

# --- Machining Parameters ---

ap = 1  #(mm)
f = 0.2 #(mm)
Vc = 150    #(m/min)
N = 1200    #(rpm)

# --- Loading Data ---

# File data CSV -> C:= cutting; NC := NON-cutting
filedataC150 = 'ANNACHPTVC150.csv'
filedataNC150 = 'ANNACHPTVC150VIDE.csv'
filedataC1200 = 'ANNACHPT1200RPM.csv'
filedataNC1200 = 'ANNACHPT1200RPMVIDE.csv'

dfC150 = pd.read_csv(filedataC150, skiprows=10)
dfNC150 = pd.read_csv(filedataNC150, skiprows=10)
dfC1200 = pd.read_csv(filedataC1200, skiprows=10)
dfNC1200 = pd.read_csv(filedataNC1200, skiprows=10)

# Naming columns
dfC150.columns = [
    'time', #(s)
    'power',    #(W)
    'prog_pos_z',   # Programmed position
    'prog_pos_x',
    'meas_pos_z',   # Actual value of position 
    'meas_pos_x',
    'spindle1'  #(rpm)  # Spindle speed. Only the first data does not have the spindle 2 data
]

cols = ['time', 'power', 'prog_pos_z', 'prog_pos_x',
        'meas_pos_z', 'meas_pos_x', 'spindle1', 'spindle2']
for df in [dfNC150, dfC1200, dfNC1200]:
    df.columns = cols

# Defining indecis of columns
cols_to_convert = dfC150.columns.difference(['time'])

# Conversion to numeric type
for df in [dfC150, dfNC150, dfC1200, dfNC1200]:
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Suppressing Nan columns
for df in [dfC150, dfNC150, dfC1200, dfNC1200]:
    df.dropna(inplace=True)

# --- Programmed position plots (before filtering) ---

fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2, 2, height_ratios=[1,1])  # 2x2 grid

# Progammed positions X vs Z
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(dfC150['prog_pos_z'], dfC150['prog_pos_x'],
         label='C150', color='brown', marker='o', linestyle='none')
ax1.plot(dfC1200['prog_pos_z'], dfC1200['prog_pos_x'],
         label='C1200', color='darkblue', marker='*', linestyle='none')
ax1.set_xlabel('Position Z (mm)')
ax1.set_ylabel('Position X Diameter (mm)')
ax1.set_title('Programmed position')

# Progammed position Z vs Time
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(dfC150['time'], dfC150['prog_pos_z'],
         label='C150', color='brown', marker='o', linestyle='none')
ax2.plot(dfC1200['time'], dfC1200['prog_pos_z'],
         label='C1200', color='darkblue', marker='*', linestyle='none')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Position Z (mm)')
ax2.set_title('Programmed Z vs. Time')

# Progammed position X Diameter vs Time
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(dfC150['time'], dfC150['prog_pos_x'],
         label='C150', color='brown', marker='o', linestyle='none')
ax3.plot(dfC1200['time'], dfC1200['prog_pos_x'],
         label='C1200', color='darkblue', marker='*', linestyle='none')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Position X Diameter (mm)')
ax3.set_title('Programmed X Diameter vs. Time')

for ax in [ax1, ax2, ax3]:
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.savefig('position_before_filter.png', dpi=DPI, bbox_inches='tight')
#plt.show()

# --- Filtering data in order to select only the cutting parts ---

dfs = {'C150': dfC150, 'NC150': dfNC150, 'C1200': dfC1200, 'NC1200': dfNC1200}

for key, df in dfs.items():
    dfs[key] = df[(df['prog_pos_x'] >= 24) &    # cutting diameter
                  (df['prog_pos_x'] <= 46) &    # cutting diameter
                  (df['prog_pos_z'] <= 0) &     # cutting feed
                  (df['prog_pos_z'] >= -40) &   # cutting feed
                  (df['prog_pos_x'] % 1 == 0)   # programmed diameter is integer
                  ]
    
filt_dfC150 = dfs['C150']
filt_dfNC150 = dfs['NC150']
filt_dfC1200 = dfs['C1200']
filt_dfNC1200 = dfs['NC1200']

# Programmed position plots
fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2,1)  # 2x2 grid

# Progammed position Z vs. Time
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(filt_dfC150['time'], filt_dfC150['prog_pos_z'],
      label='C150', color='brown', marker='o', linestyle='none')
ax1.plot(filt_dfC1200['time'], filt_dfC1200['prog_pos_z'],
      label='C1200', color='darkblue', marker='*', linestyle='none')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Position Z (mm)')
ax1.set_title('Programmed Z vs. Time')

# Progammed position X Diameter vs. Time
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(filt_dfC150['time'], filt_dfC150['prog_pos_x'],
      label='C150', color='brown', marker='o', linestyle='none')
ax2.plot(filt_dfC1200['time'], filt_dfC1200['prog_pos_x'],
      label='C1200', color='darkblue', marker='*', linestyle='none')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Position X Diameter (mm)')
ax2.set_title('Programmed X Diameter vs.. Time')

for ax in [ax1, ax2]:
    ax.grid(True)
    ax.legend()
plt.tight_layout()

plt.savefig('programmed_positions_150_1200.png', dpi=DPI, bbox_inches='tight')
#plt.show()

# --- Power plots ---

# Overall figure
fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2, 1)

# Power vs. Time using constant cutting velocity
ax1 = fig.add_subplot(gs[0,0])
ax1.plot(filt_dfC150['time'], filt_dfC150['power'], label='C150', color='brown') 
ax1.plot(filt_dfNC150['time'], filt_dfNC150['power'], label='NC150', color='darkblue')
#ax1.set_xlim(25,28)
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Spindle Power (W)')
ax1.set_title('Power vs. Time at Constant Cutting Speed (150 m/min)')

# Power vs. Time using constant spindle speed
ax2 = fig.add_subplot(gs[1,0])
ax2.plot(filt_dfC1200['time'], filt_dfC1200['power'], label='C1200', color='brown') 
ax2.plot(filt_dfNC1200['time'], filt_dfNC1200['power'], label='NC1200', color='darkblue')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Spindle Power (W)')
ax2.set_title('Power vs. Time at Constant Spindle Speed (1200 rpm)')

for ax in [ax1, ax2]:
    ax.grid(True)
    ax.legend()
plt.tight_layout()

plt.savefig('power_vs_time_150_1200.png', dpi=DPI, bbox_inches='tight')
#plt.show()

# --- Filtering data to avoid power peaks ---

dfs = {'C150': filt_dfC150, 'NC150': filt_dfNC150, 'C1200': filt_dfC1200, 'NC1200': filt_dfNC1200}
cleaned_dfs = {}

for key, df in dfs.items():
    mean_power = df.groupby('prog_pos_x')['power'].mean()
    std_power = df.groupby('prog_pos_x')['power'].std()

    df = df.copy()
    df['mean_power'] = df['prog_pos_x'].map(mean_power)
    df['std_power'] = df['prog_pos_x'].map(std_power)

    # Mask: keep just elements in [mean + std, mean - std]
    mask = (df['power'] > df['mean_power'] - 2 * df['std_power']) & \
           (df['power'] < df['mean_power'] + 2 * df['std_power'])
    df_clean = df[mask].drop(columns=['mean_power', 'std_power'])

    cleaned_dfs[key] = df_clean

filt_dfC150_new = cleaned_dfs['C150']
filt_dfNC150_new = cleaned_dfs['NC150']
filt_dfC1200_new = cleaned_dfs['C1200']
filt_dfNC1200_new = cleaned_dfs['NC1200']

# Filtered power plot
fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2, 1)

# Power vs. Time using constant cutting velocity
ax1 = fig.add_subplot(gs[0,0])
ax1.plot(filt_dfC150_new['time'], filt_dfC150_new['power'], label='C150', color='brown') 
ax1.plot(filt_dfNC150_new['time'], filt_dfNC150_new['power'], label='NC150', color='darkblue')
#ax1.set_xlim(0,20)
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Spindle Power (W)')
ax1.set_title('Power vs. Time at Constant Cutting Speed (150 m/min)')

# Power vs. Time using constant spindle speed
ax2 = fig.add_subplot(gs[1,0])
ax2.plot(filt_dfC1200_new['time'], filt_dfC1200_new['power'], label='C1200', color='brown') 
ax2.plot(filt_dfNC1200_new['time'], filt_dfNC1200_new['power'], label='NC1200', color='darkblue')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Spindle Power (W)')
ax2.set_title('Power vs. Time at Constant Spindle Speed (1200 rpm)')

for ax in [ax1, ax2]:
    ax.grid(True)
    ax.legend()
plt.tight_layout()

plt.savefig('power_vs_time_150_1200_v2.png', dpi=DPI, bbox_inches='tight')
#plt.show()

# Plot focused on the power transitory
plt.figure(figsize=(10,8))
plt.plot(filt_dfC150_new['time'], filt_dfC150_new['power'], label='C150', color='brown') 
plt.plot(filt_dfNC150_new['time'], filt_dfNC150_new['power'], label='NC150', color='darkblue')
plt.xlim(0,20)
plt.xlabel('Time (s)')
plt.ylabel('Spindle Power (W)')
plt.title('Power vs. Time at Constant Cutting Speed (150 m/min)')

plt.scatter(3.5, 1500, s=20000, facecolors='none', edgecolors='#3CB371', linewidths=2.5, zorder=10)

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig('focus_power.png', dpi=DPI, bbox_inches='tight')
#plt.show()

# --- C150: excluding elements until t = 4 ---
filt_dfC150_new = filt_dfC150_new[filt_dfC150_new['time'] > 4]

# Re-definition of filtered data frames
filt_dfC150 = filt_dfC150_new
filt_dfNC150 = filt_dfNC150_new
filt_dfC1200 = filt_dfC1200_new
filt_dfNC1200 = filt_dfNC1200_new

# --- Cutting Power Calculation ---

df_150 = pd.DataFrame({
    'time' : filt_dfC150['time'],
    'prog_pos_x' : filt_dfC150['prog_pos_x'],
    'Pc': filt_dfC150['power'] - filt_dfNC150['power']
}).dropna()
df_1200 = pd.DataFrame({
    'time' : filt_dfC1200['time'],
    'prog_pos_x' : filt_dfC1200['prog_pos_x'],
    'Pc': filt_dfC1200['power'] - filt_dfNC1200['power']
}).dropna()

# --- Constant Cutting Speed Analysis ---

# Cutting Force
df_150['Fc'] = df_150['Pc'] / Vc * 60   #(N)

# Specific Cutting Force
df_150['Kc'] = df_150['Fc'] / (ap * f)   #(N/mm² = MPa)

stats_150 = (
    df_150.groupby('prog_pos_x')[['Pc', 'Fc', 'Kc']]
    .agg(['min', 'max', 'mean', 'std'])
    .reset_index()
    .sort_values(by='prog_pos_x', ascending=False)
)

stats_150.to_csv("stats_150.csv", index=False, sep=",", float_format="%.1f")

# Plot of cutting power for each X diameter
diameters = sorted(df_150['prog_pos_x'].unique(), reverse=True)

n_diam = len(diameters)
n_cols = 4
n_rows = int(np.ceil(n_diam / n_cols))

fig = plt.figure(figsize=(15, n_rows * 3))   # 15 inches wide, auto height scaling
gs = gridspec.GridSpec(n_rows, n_cols)

# Loop through each diameter
for i, x in enumerate(diameters):
    ax = fig.add_subplot(gs[i // n_cols, i % n_cols])

    # Filter data for this diameter
    subset = df_150[df_150['prog_pos_x'] == x].copy()
    subset['Pc'] = subset['Pc'] / 1000

    mean_x = stats_150.loc[stats_150['prog_pos_x'] == x, ('Pc','mean')].values[0] / 1000
    std_x = stats_150.loc[stats_150['prog_pos_x'] == x, ('Pc','std')].values[0] / 1000

    ax.plot(subset['time'], subset['Pc'], color='gray', alpha=0.4, label='Measured Power')
    ax.axhline(mean_x, color='red', linestyle='-.', label='Mean Power')
    ax.fill_between(subset['time'],
                    mean_x - std_x, mean_x + std_x,
                    color='red', alpha=0.2, label='±σ')

    ax.set_title(f"X = {x:.0f} mm", fontsize=9)
    ax.set_xlabel("Time (s)", fontsize=8)
    ax.set_ylabel("Cutting Power (kW)", fontsize=8)
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=7)

# Remove any empty subplots if grid > number of diameters
for j in range(i + 1, n_rows * n_cols):
    fig.delaxes(fig.axes[j])

# Global figure title and legend
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels,
           loc='lower center',
           bbox_to_anchor=(0.5, -0.02),  # outside bottom margin
           ncol=3,
           frameon=False)
fig.suptitle("Cutting Power vs. Time for Each Programmed Position Diameter X", fontsize=14, fontweight='bold')
fig.text(0.5, 0.93, "Constant Cutting Speed at 150 m/min",
         ha='center', fontsize=12, style='italic', color='dimgray')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('pc_vs_time_diam.png', dpi=DPI, bbox_inches='tight')
#plt.show()

# --- Constant Speed Spindle Analysis ---

# Cutting speed
df_1200['Vc'] = N * np.pi * df_1200['prog_pos_x'] / 1000    #(m/min) 

# Cutting Force
df_1200['Fc'] = df_1200['Pc'] / df_1200['Vc'] * 60   #(N)

# Specific Cutting Force
df_1200['Kc'] = df_1200['Fc'] / (ap * f)   #(N/mm² = MPa)

stats_1200 = (
    df_1200.groupby('prog_pos_x')[['Pc', 'Fc', 'Kc']]
    .agg(['min', 'max', 'mean', 'std'])
    .reset_index()
    .sort_values(by='prog_pos_x', ascending=False)
)

stats_1200.to_csv("stats_1200.csv", index=False, sep=",", float_format="%.1f")

fig = plt.figure(figsize=(15, n_rows * 3))   # 15 inches wide, auto height scaling
gs = gridspec.GridSpec(n_rows, n_cols)

# Loop through each diameter
for i, x in enumerate(diameters):
    ax = fig.add_subplot(gs[i // n_cols, i % n_cols])

    # Filter data for this diameter
    subset = df_1200[df_1200['prog_pos_x'] == x].copy()
    subset['Pc'] = subset['Pc'] / 1000

    mean_x = stats_1200.loc[stats_1200['prog_pos_x'] == x, ('Pc','mean')].values[0] / 1000
    std_x = stats_1200.loc[stats_1200['prog_pos_x'] == x, ('Pc','std')].values[0] / 1000

    # Plot
    ax.plot(subset['time'], subset['Pc'], color='gray', alpha=0.4, label='Measured Power')
    ax.axhline(mean_x, color='red', linestyle='-.', label='Mean Power')
    ax.fill_between(subset['time'],
                    mean_x - std_x, mean_x + std_x,
                    color='red', alpha=0.2, label='±σ')

    # Labels and formatting
    ax.set_title(f"X = {x:.0f} mm", fontsize=9)
    ax.set_xlabel("Time (s)", fontsize=8)
    ax.set_ylabel("Cutting Power (kW)", fontsize=8)
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=7)

# Remove any empty subplots if grid > number of diameters
for j in range(i + 1, n_rows * n_cols):
    fig.delaxes(fig.axes[j])

# Global figure title and legend
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels,
           loc='lower center',
           bbox_to_anchor=(0.5, -0.02),  # outside bottom margin
           ncol=3,
           frameon=False)
fig.suptitle("Cutting Power vs. Time for Each Programmed Position Diameter X", fontsize=14, fontweight='bold')
fig.text(0.5, 0.93, "Constant Spindle Speed at 1200 rpm",
         ha='center', fontsize=12, style='italic', color='dimgray')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('pc_vs_time_diam_1200.png', dpi=DPI, bbox_inches='tight')
#plt.show()