import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import numpy as np

# ---- PARAMETERS ----

D = 63  #(mm)
Vc = 150    #(m/min)
N = Vc/(np.pi * D) * 1000

# ---- FILES UPLOAD ----

fileSession5A1A = "data/Session5A1A.csv" # NON-cutting
fileSession5A1B = "data/Session5A1B.csv" # cutting

df5A1A = pd.read_csv(fileSession5A1A, skiprows=9)
df5A1A = df5A1A.iloc[:, :-1]
df5A1A = df5A1A.apply(pd.to_numeric, errors='coerce')
df5A1A = df5A1A.dropna()

df5A1B = pd.read_csv(fileSession5A1B, skiprows=9)
df5A1B = df5A1B.iloc[:, :-1]
df5A1B = df5A1B.apply(pd.to_numeric, errors='coerce')
df5A1B = df5A1B.dropna()

# Naming columns
cols = ['time', 'prog_pos_x', 'meas_pos_x', 'power', 'prog_pos_y', 'meas_pos_y','prog_pos_z', 'meas_pos_z']
for df in [df5A1A, df5A1B]:
    df.columns = cols

# ---- Cutting Power (of the entire process) ----

# Calculate the cutting power at the SAME instant time, otherwise insert a Nan in the result
df150 = (df5A1B.set_index('time')['power'] - df5A1A.set_index('time')['power'])

df150 = df150.reset_index(name='power')

fig, axes = plt.subplots(2, 1, figsize=(12, 10))

axes[0].plot(df5A1B['time'], df5A1B['power'], marker='.', linestyle='none')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Power (W)')
axes[0].set_title('Power vs. Time - Cutting Session')
axes[0].grid(True)

axes[1].plot(df150['time'], df150['power'], marker='.', linestyle='none')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Cutting Power (W)')
axes[1].set_title('Cutting Power vs. Time - Cutting Session')
axes[1].grid(True)

plt.tight_layout()
plt.savefig("plots/powerS.png", dpi=300, bbox_inches='tight')
#plt.show()
plt.close(fig) 

# ---- Surface Milling ----

# Redefinition of surfacing part
df150 = df5A1B[['time', 'power']].copy()    # entire cutting session
df150 = df150[(df150['time'] >= 18) & (df150['time'] <= 80)]

# Revolution counter (just in the surfacing interval!)
Trev = 60/N # (s) revolution period
df150['rev'] = ((df150['time'] - df150['time'].iloc[0])/Trev).astype(int)
df150.insert(0, 'rev', df150.pop('rev'))

fig, axes = plt.subplots(2, 1, figsize=(12, 10))

axes[0].plot(df150['time'], df150['power'], marker='.', linestyle='none')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Power (W)')
axes[0].set_title('Power vs. Time - Surface Milling')
axes[0].grid(True)

axes[1].plot(df150['rev'], df150['power'], marker='.', linestyle='none')
axes[1].set_xlabel('Revolutions')
axes[1].set_ylabel('Power (W)')
axes[1].set_title('Power vs. Revolutions - Surface Milling')
axes[1].grid(True)

plt.tight_layout()
plt.savefig("plots/surf.png", dpi=300, bbox_inches='tight')
#plt.show()
plt.close()

# ---- Power Statistics ----

stats = df150.groupby('rev')['power'].agg(
    mean_power='mean',
    min_power='min',
    max_power='max'
).reset_index()


stats.to_csv("plots/stats_rev.csv", index=False)


fig, axes = plt.subplots(3, 1, figsize=(12, 12))
fig.subplots_adjust(hspace=0.4)

axes[0].plot(stats['rev'], stats['mean_power'], marker='.')
#axes[0].set_xlabel('Revolutions')
axes[0].set_ylabel('Mean Power (W)')
axes[0].set_title('Mean Power per Revolution')
axes[0].grid(True)

axes[1].plot(stats['rev'], stats['min_power'], marker='.', color='green')
#axes[1].set_xlabel('Revolutions')
axes[1].set_ylabel('Min Power (W)')
axes[1].set_title('Minimum Power per Revolution')
axes[1].grid(True)

axes[2].plot(stats['rev'], stats['max_power'], marker='.', color='red')
axes[2].set_xlabel('Revolutions')
axes[2].set_ylabel('Max Power (W)')
axes[2].set_title('Maximum Power per Revolution')
axes[2].grid(True)

plt.tight_layout()
plt.savefig("plots/pow_stats.png", dpi=300, bbox_inches='tight')
#plt.show()
plt.close(fig) 

# ---- Energy Consumption ----

# Trapezoidal rule
energy_per_rev = []

for rev_id, group in df150.groupby('rev'):
    t = group['time'].values
    p = group['power'].values
    
    dt = t[1:] - t[:-1]                  # Δt_j
    p_avg = (p[1:] + p[:-1]) / 2         # (P_j + P_{j+1})/2
    
    E = (p_avg * dt).sum()
    
    energy_per_rev.append([rev_id, E])

energy_per_rev = pd.DataFrame(energy_per_rev, columns=['rev', 'energy'])


plt.plot(energy_per_rev['rev'], energy_per_rev['energy'], marker='.', linestyle='-')
plt.xlabel('Revolutions')
plt.ylabel('Energy (J)')
plt.title('Energy per Revolution')
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/energy.png", dpi=300, bbox_inches='tight')
#plt.show()