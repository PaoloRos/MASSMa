from pathlib import Path
import sys

# Scripts start from their location; interactive cells start from the working directory.
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

from repo_settings import configure_plots

configure_plots()

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker


# File data CSV
filedataC150 = 'ANNACHPTVC150.csv'
filedataNC150 = 'ANNACHPTVC150VIDE.csv'
filedataC1200 = 'ANNACHPT1200RPM.csv'
filedataNC1200 = 'ANNACHPT1200RPMVIDE.csv'

# Reading csv
dfC150 = pd.read_csv(filedataC150, skiprows=10)
dfNC150 = pd.read_csv(filedataNC150, skiprows=10)
dfC1200 = pd.read_csv(filedataC1200, skiprows=10)
dfNC1200 = pd.read_csv(filedataNC1200, skiprows=10)

# # Columns names / Same for all data
dfC150.columns = [
    'time',
    'power',
    'prog_pos_z',
    'prog_pos_x',
    'meas_pos_z',
    'meas_pos_x',
    'spindle1' # only the first data does not have the spindle 2 data
]
dfNC150.columns = [
    'time',
    'power',
    'prog_pos_z',
    'prog_pos_x',
    'meas_pos_z',
    'meas_pos_x',
    'spindle1',
    'spindle2'
]
dfC1200.columns = [
    'time',
    'power',
    'prog_pos_z',
    'prog_pos_x',
    'meas_pos_z',
    'meas_pos_x',
    'spindle1',
    'spindle2'
]
dfNC1200.columns = [
    'time',
    'power',
    'prog_pos_z',
    'prog_pos_x',
    'meas_pos_z',
    'meas_pos_x',
    'spindle1',
    'spindle2'
]

cols_to_convert = dfC150.columns.difference(['time'])  # or specify manually

# # Conversion 
# for col in df.columns:
for df in [dfC150, dfNC150, dfC1200, dfNC1200]:
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        

# # Suppression des lignes incomplètes
# # 
dfC150 = dfC150.dropna()
dfNC150 = dfNC150.dropna()
dfC1200 = dfC1200.dropna()
dfNC1200 = dfNC1200.dropna()

# ####################################################
# # Calculating dt
dfC150['delta_t'] = dfC150['time'].diff()
dfC150['delta_t'].iloc[0] = 0  # Premier delta_t = 0

dfNC150['delta_t'] = dfNC150['time'].diff()
dfNC150['delta_t'].iloc[0] = 0  # Premier delta_t = 0

dfC1200['delta_t'] = dfC1200['time'].diff()
dfC1200['delta_t'].iloc[0] = 0  # Premier delta_t = 0

dfNC1200['delta_t'] = dfNC1200['time'].diff()
dfNC1200['delta_t'].iloc[0] = 0  # Premier delta_t = 0

# ####################################################
# # Calculating Instantaneos energy (W × s / 1000 = kJ)
# # df['energy_kJ'] = df['power'] * df['delta_t'] / 1000

dfC150['energy_kJ'] = dfC150['power'] * dfC150['delta_t'] / 1000
dfNC150['energy_kJ'] = dfNC150['power'] * dfNC150['delta_t'] / 1000
dfC1200['energy_kJ'] = dfC1200['power'] * dfC1200['delta_t'] / 1000
dfNC1200['energy_kJ'] = dfNC1200['power'] * dfNC1200['delta_t'] / 1000


# # Accumulated energy 
# #df['energy_kJ_cum'] = df['energy_kJ'].cumsum()

dfC150['energy_kJ_cum'] = dfC150['energy_kJ'].cumsum()
dfNC150['energy_kJ_cum'] = dfNC150['energy_kJ'].cumsum()

dfC1200['energy_kJ_cum'] = dfC1200['energy_kJ'].cumsum()
dfNC1200['energy_kJ_cum'] = dfNC1200['energy_kJ'].cumsum()


# Group energy by programmed X position
energy_by_x_C150 = dfC150.groupby('prog_pos_x')['energy_kJ'].sum().reset_index() 
Filt_energy_by_x_C150 = energy_by_x_C150[energy_by_x_C150['energy_kJ'] > 0.15]

energy_by_x_NC150 = dfNC150.groupby('prog_pos_x')['energy_kJ'].sum().reset_index()
Filt_energy_by_x_NC150 = energy_by_x_NC150[energy_by_x_NC150['energy_kJ'] > 0.15]

energy_by_x_C1200 = dfC1200.groupby('prog_pos_x')['energy_kJ'].sum().reset_index()
Filt_energy_by_x_C1200 = energy_by_x_C1200[energy_by_x_C1200['energy_kJ'] > 0.15]

energy_by_x_NC1200 = dfNC1200.groupby('prog_pos_x')['energy_kJ'].sum().reset_index()
Filt_energy_by_x_NC1200 = energy_by_x_NC1200[energy_by_x_NC1200['energy_kJ'] > 0.15]

# ####################################################
plt.figure()
# Plot C150
plt.plot(dfC150['prog_pos_z'], dfC150['prog_pos_x'], label='C150', color='brown',marker='o', linestyle='None') #linestyle='-')
# Plot NC150
plt.plot(dfC1200['prog_pos_z'], dfC1200['prog_pos_x'], label='C1200', color='darkblue',marker='*', linestyle='None') #linestyle='-')
plt.xlabel('Position Z (mm)')
plt.ylabel('Position X Diameter (mm)')
plt.title('Programmed position (150 vs 1200)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()



# ========= GRAPHE Power =========
plt.figure()
# Plot C150
plt.plot(dfC150['time'], dfC150['power'], label='C150', color='brown') 
# Plot NC150
plt.plot(dfNC150['time'], dfNC150['power'], label='NC150', color='darkblue')
plt.xlabel('Time (s)')
plt.ylabel('Spindle Power (W)')
plt.title('Spindle Power vs Time using 150 m/min (C150 vs NC150)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(dfC1200['time'], dfC1200['power'], label='C1200', color='brown')
plt.plot(dfNC1200['time'], dfNC1200['power'], label='NC1200', color='darkblue')
plt.xlabel('Time (s)')
plt.ylabel('Spindle Power (W)')
plt.title('Spindle Power vs Time using 1200 rev/min (C1200 vs NC1200)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
# ####################################################

# Accumulated energy vs Time kJ
plt.plot(dfC150['time'], dfC150['energy_kJ_cum'] / 3600, label='Vc=150',color='blue', linestyle='-')
plt.plot(dfC1200['time'], dfC1200['energy_kJ_cum'] / 3600, label='N=1200',color='green', linestyle='-')
plt.plot(dfNC150['time'], dfNC150['energy_kJ_cum'] / 3600, label='Vc=150 no cutting',color='blue', linestyle='--')
plt.plot(dfNC1200['time'], dfNC1200['energy_kJ_cum'] / 3600, label='N=1200 no cutting',color='green', linestyle='--')
plt.xlabel('Time (s)')
plt.ylabel('Energy (kJ)')
plt.title('Accumulated energy vs Time')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

plt.plot(dfC150['time'], dfC150['energy_kJ_cum'] / 3600, label='Vc=150',color='blue', linestyle='-')
plt.plot(dfC1200['time'], dfC1200['energy_kJ_cum'] / 3600, label='N=1200',color='green', linestyle='-')
plt.plot(dfNC150['time'], dfNC150['energy_kJ_cum'] / 3600, label='Vc=150 no cutting',color='blue', linestyle='--')
plt.plot(dfNC1200['time'], dfNC1200['energy_kJ_cum'] / 3600, label='N=1200 no cutting',color='green', linestyle='--')
plt.xlabel('Time (s)')
plt.ylabel('Energy (kWh)')
plt.title('Accumulated energy vs Time')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Plotting
plt.figure()
plt.plot(Filt_energy_by_x_C150['prog_pos_x'], Filt_energy_by_x_C150['energy_kJ'],linestyle='None', marker='o', label='C150')
plt.plot(Filt_energy_by_x_NC150['prog_pos_x'], Filt_energy_by_x_NC150['energy_kJ'],linestyle='None', marker='*', label='NC150')
plt.plot(Filt_energy_by_x_C1200['prog_pos_x'], Filt_energy_by_x_C1200['energy_kJ'],linestyle='None', marker='o', label='C1200')
plt.plot(Filt_energy_by_x_NC1200['prog_pos_x'], Filt_energy_by_x_NC1200['energy_kJ'],linestyle='None', marker='*', label='NC1200')
plt.xlabel('Programmed Position in X (Diameter in mm)')
plt.ylabel('Energy Used in this position (kJ)')
plt.title('Energy at Each Position X')
plt.xlim(23, 47)
# Set Y-axis grid every 1 unit
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
# Add grid
plt.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
plt.grid(True, which='major', axis='x', linestyle='--', linewidth=0.4, alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()

# Intervalles
interval_starts150 = [6, 18, 30, 41, 51, 61, 71, 80, 89, 97, 105, 112]
interval_dfsC150 = {}
interval_dfsNC150 = {}
mean_powersC150 = {}
mean_powersNC150 = {}

for i, start_time in enumerate(interval_starts150, start=1):
    end_time = start_time + 5
    maskC = (dfC150['time'] >= start_time) & (dfC150['time'] <= end_time)
    interval_dfC150 = dfC150[maskC]

    maskNC = (dfNC150['time'] >= start_time) & (dfNC150['time'] <= end_time)
    interval_dfNC150 = dfNC150[maskNC]

    interval_dfsC150[f'intv{i}'] = interval_dfC150
    interval_dfsNC150[f'intv{i}'] = interval_dfNC150

    mean_powerC150 = interval_dfC150['power'].mean()
    mean_powerNC150 = interval_dfNC150['power'].mean()

    mean_powersC150[f'intv{i}'] = mean_powerC150  # ✅ bonne affectation
    mean_powersNC150[f'intv{i}'] = mean_powerNC150

    print(f'Interval {i}: {start_time}s to {end_time}s, Mean Power Cutting = {mean_powerC150:.2f} W')
    print(f'Interval {i}: {start_time}s to {end_time}s, Mean Power No Cutting = {mean_powerNC150:.2f} W')

# Création des listes
labels = list(mean_powersC150.keys())
mean_values_C = list(mean_powersC150.values())
mean_values_NC = list(mean_powersNC150.values())

# Largeur des barres
bar_width = 0.4
x = np.arange(len(labels))  # positions x

# Tracer les barres
plt.figure()
bars_C = plt.bar(x - bar_width/2, mean_values_C, width=bar_width, color='skyblue', label='Cutting')
bars_NC = plt.bar(x + bar_width/2, mean_values_NC, width=bar_width, color='lightgreen', label='No Cutting')

plt.xlabel('Cutting passes')
plt.ylabel('Mean Power (W)')
plt.title('Mean Power per 5-second Interval (Vc=150)')
plt.xticks(x, labels, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()

# Afficher les valeurs au-dessus des barres
for bar in bars_C:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom', fontsize=8)
for bar in bars_NC:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()

interval_starts1200 = [5, 14, 24, 33, 46, 56, 67, 78, 88, 98, 110, 120]

interval_dfsC1200 = {}
interval_dfsNC1200 = {}
mean_powersC1200 = {}
mean_powersNC1200 = {}

for i, start_time in enumerate(interval_starts1200, start=1):
    end_time = start_time + 5
    maskC = (dfC1200['time'] >= start_time) & (dfC1200['time'] <= end_time)
    interval_dfC1200 = dfC1200[maskC]

    maskNC = (dfNC1200['time'] >= start_time) & (dfNC1200['time'] <= end_time)
    interval_dfNC1200 = dfNC1200[maskNC]

    interval_dfsC1200[f'intv{i}'] = interval_dfC1200
    interval_dfsNC1200[f'intv{i}'] = interval_dfNC1200

    mean_powerC1200 = interval_dfC1200['power'].mean()
    mean_powerNC1200 = interval_dfNC1200['power'].mean()

    mean_powersC1200[f'intv{i}'] = mean_powerC1200
    mean_powersNC1200[f'intv{i}'] = mean_powerNC1200

    print(f'Interval {i}: {start_time}s to {end_time}s, Mean Power Cutting = {mean_powerC1200:.2f} W')
    print(f'Interval {i}: {start_time}s to {end_time}s, Mean Power No Cutting = {mean_powerNC1200:.2f} W')

# Plotting
labels = list(mean_powersC1200.keys())
mean_values_C = list(mean_powersC1200.values())
mean_values_NC = list(mean_powersNC1200.values())

bar_width = 0.4
x = np.arange(len(labels))

plt.figure()
bars_C = plt.bar(x - bar_width/2, mean_values_C, width=bar_width, color='skyblue', label='Cutting')
bars_NC = plt.bar(x + bar_width/2, mean_values_NC, width=bar_width, color='lightgreen', label='No Cutting')

plt.xlabel('Cutting passes')
plt.ylabel('Mean Power (W)')
plt.title('Mean Power per 5-second Interval (N=1200)')
plt.xticks(x, labels, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()

# Add values on top
for bar in bars_C:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom', fontsize=8)
for bar in bars_NC:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()

# Build the table
mean_power_table = pd.DataFrame({
    'Interval': list(mean_powersC150.keys()),
    'Vc=150 Cutting': list(mean_powersC150.values()),
    'Vc=150 No Cutting': list(mean_powersNC150.values()),
    'Vc=1200 Cutting': list(mean_powersC1200.values()),
    'Vc=1200 No Cutting': list(mean_powersNC1200.values())
})

# Optional: Set Interval as index
mean_power_table.set_index('Interval', inplace=True)

# Show table in console
print(mean_power_table)

# Export to CSV
mean_power_table.to_csv('mean_powers_summary.csv')