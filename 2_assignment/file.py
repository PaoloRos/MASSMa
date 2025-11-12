# Importing libraries
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # forza un backend interattivo compatibile su macOS
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import numpy as np

D = 10  #(mm)
a_p = 1 #(mm)
fz = 0.05   #(mm/rev)
z = 2
Vc = 150    #m/min
N = Vc/(np.pi * D) * 1000
Vf = fz*z*N

fileSession5A1A = "Analyse Usinage/Session5A1A.csv"
fileSession5A1B = "Analyse Usinage/Session5A1B.csv"

df5A1A = pd.read_csv(fileSession5A1A, skiprows=9)
df5A1B = pd.read_csv(fileSession5A1B, skiprows=9)

# Naming columns
cols = ['time', 'prog_pos_x', 'meas_pos_x', 'power', 'prog_pos_y', 'meas_pos_y','prog_pos_z', 'meas_pos_z', 'niente']
for df in [df5A1A, df5A1B]:
    df.columns = cols

df5A1A = df5A1A.drop('niente', axis=1)
df5A1B = df5A1B.drop('niente', axis=1)

# --- Modalità interattiva ---
plt.ion()

# --- Crea figura 3D ---
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(
    df5A1A['prog_pos_x'],
    df5A1A['prog_pos_y'],
    df5A1A['prog_pos_z'],
    c='r', marker='o'
)

# --- Etichette ---
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Traiettoria utensile 3D')

plt.tight_layout()
plt.show(block=True)  # mantiene la finestra aperta