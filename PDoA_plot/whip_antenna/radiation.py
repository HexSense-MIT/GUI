import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Get all CSV files in the current directory
csv_files = sorted(glob.glob('*.csv'), key=lambda x: int(x.split('.')[0]))

# Read and process all CSV files
all_data = []
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        angle = int(csv_file.split('.')[0])

        # Calculate mean for PDoA and AoA
        pdoa_mean = df['PDoA'].mean()
        aoa_mean = df['AoA'].mean()

        all_data.append({
            'angle': angle * 22.5,  # Convert filename to degrees
            'pdoa_mean': pdoa_mean,
            'aoa_mean': aoa_mean
        })
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")

# Convert to DataFrame
results_df = pd.DataFrame(all_data)
results_df = results_df.sort_values('angle')

# Convert angles to radians for polar plot
# Angles range from -180 to 180 degrees
angles_rad = np.radians(results_df['angle'].values)

# Create Figure 1: PDoA Radiation Pattern
fig1 = plt.figure(figsize=(10, 10))
ax1 = fig1.add_subplot(111, projection='polar')

# Plot PDoA radiation pattern
ax1.plot(angles_rad, results_df['pdoa_mean'], 'o-', linewidth=2, markersize=8)
ax1.fill(angles_rad, results_df['pdoa_mean'], alpha=0.25)
ax1.set_theta_zero_location('E')  # 0 degrees at East (right)
ax1.set_theta_direction(1)  # Counter-clockwise: positive angles go left
ax1.set_thetamin(-180)
ax1.set_thetamax(180)
ax1.set_title('PDoA Radiation Pattern', fontsize=14, pad=20)
ax1.grid(True)

# Create Figure 2: AoA Radiation Pattern
fig2 = plt.figure(figsize=(10, 10))
ax2 = fig2.add_subplot(111, projection='polar')

# Plot AoA radiation pattern
ax2.plot(angles_rad, results_df['aoa_mean'], 's-', linewidth=2, markersize=8, color='orange')
ax2.fill(angles_rad, results_df['aoa_mean'], alpha=0.25, color='orange')
ax2.set_theta_zero_location('E')  # 0 degrees at East (right)
ax2.set_theta_direction(1)  # Counter-clockwise: positive angles go left
ax2.set_thetamin(-180)
ax2.set_thetamax(180)
ax2.set_title('AoA Radiation Pattern', fontsize=14, pad=20)
ax2.grid(True)

plt.tight_layout()
plt.show()

# Print the data
print("\nRadiation Pattern Data:")
print(results_df.to_string(index=False))
