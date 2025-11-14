import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import numpy as np

# ---- PARAMETERS ----

D = 5.5  #(mm)
Vc = 150    #(m/min)
N = Vc/(np.pi * D) * 1000

# ---- FILES UPLOAD ----

fileSession5A1A = "Analyse Usinage/Session5A1A.csv" # NON-cutting
fileSession5A1B = "Analyse Usinage/Session5A1B.csv" # cutting

df5A1A = pd.read_csv(fileSession5A1A, skiprows=9)
df5A1A = df5A1A.iloc[:, :-1]
df5A1A = df5A1A.dropna()

df5A1B = pd.read_csv(fileSession5A1B, skiprows=9)
df5A1B = df5A1B.iloc[:, :-1]
df5A1B = df5A1B.dropna()

# Naming columns
cols = ['time', 'prog_pos_x', 'meas_pos_x', 'power', 'prog_pos_y', 'meas_pos_y','prog_pos_z', 'meas_pos_z']
for df in [df5A1A, df5A1B]:
    df.columns = cols

# ---- Power plot ----

plt.plot(df5A1B['time'], df5A1B['power'], marker = '.', linestyle='none')
plt.xlabel('Time (s)')
plt.ylabel('Power (W)')
plt.title('Power vs Time - Cutting')
plt.grid(True)
plt.tight_layout()
plt.show()