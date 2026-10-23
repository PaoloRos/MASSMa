import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Given parameters
Vc = 150  # cutting speed in m/min

# Diameters in mm from 24 to 46
diameters = np.array([24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46])

# Calculate spindle speed in rpm
spindle_speed = (1000 * Vc) / (np.pi * diameters)



# Print results
for d, n in zip(diameters, spindle_speed):
    print(f"Diameter: {d} mm -> Spindle Speed: {n:.0f} rpm")

# Plotting
plt.figure(figsize=(8, 4))
plt.plot(diameters, spindle_speed, marker='o', linestyle='--', color='green')
plt.xlabel('Diameter (mm)')
plt.ylabel('Spindle Speed (rpm)')
plt.title('Spindle Speed vs Diameter at 150 m/min')
plt.grid(True)
plt.tight_layout()
plt.show()


# Fixed spindle speed
N = 1200  # rpm

# Cutting speed calculation (in m/min)
Vc = (np.pi * diameters * N) / 1000

# Print results
for d, v in zip(diameters, Vc):
    print(f"Diameter: {d} mm -> Cutting Speed: {v:.2f} m/min")

# Plotting
plt.figure(figsize=(8, 4))
plt.plot(diameters, Vc, marker='s', linestyle='-', color='blue')
plt.xlabel('Diameter (mm)')
plt.ylabel('Cutting Speed (m/min)')
plt.title('Cutting Speed vs Diameter at 1200 rpm')
plt.grid(True)
plt.tight_layout()
plt.show()