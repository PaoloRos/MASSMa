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
import numpy as np

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

# --- Programmed position plots ---

fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2,1)  # 2x2 grid

# Progammed position Z vs Time
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(filt_dfC150['time'], filt_dfC150['prog_pos_z'],
      label='C150', color='brown', marker='o', linestyle='none')
ax1.plot(filt_dfC1200['time'], filt_dfC1200['prog_pos_z'],
      label='C1200', color='darkblue', marker='*', linestyle='none')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Position Z (mm)')
ax1.set_title('Programmed Z vs Time')

# Progammed position X Diameter vs Time
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(filt_dfC150['time'], filt_dfC150['prog_pos_x'],
      label='C150', color='brown', marker='o', linestyle='none')
ax2.plot(filt_dfC1200['time'], filt_dfC1200['prog_pos_x'],
      label='C1200', color='darkblue', marker='*', linestyle='none')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Position X Diameter (mm)')
ax2.set_title('Programmed X Diameter vs Time')

for ax in [ax1, ax2]:
    ax.grid(True)
    ax.legend()
plt.tight_layout()

plt.savefig('programmed_positions_150_1200.png', dpi=600, bbox_inches='tight')
plt.show()

# --- Power plots ---

# Overall figure
fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2, 1)

# Power vs Time using constant cutting velocity
ax1 = fig.add_subplot(gs[0,0])
ax1.plot(filt_dfC150['time'], filt_dfC150['power'], label='C150', color='brown') 
ax1.plot(filt_dfNC150['time'], filt_dfNC150['power'], label='NC150', color='darkblue')
#ax1.set_xlim(25,28)
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Spindle Power (W)')
ax1.set_title('Power vs Time at Constant Cutting Speed (150 m/min)')

# Power vs Time using constant spindle speed
ax2 = fig.add_subplot(gs[1,0])
ax2.plot(filt_dfC1200['time'], filt_dfC1200['power'], label='C1200', color='brown') 
ax2.plot(filt_dfNC1200['time'], filt_dfNC1200['power'], label='NC1200', color='darkblue')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Spindle Power (W)')
ax2.set_title('Power vs Time at Constant Spindle Speed (1200 rpm)')

for ax in [ax1, ax2]:
    ax.grid(True)
    ax.legend()
plt.tight_layout()

plt.savefig('power_vs_time_150_1200.png', dpi=600, bbox_inches='tight')
plt.show()