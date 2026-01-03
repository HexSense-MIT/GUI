import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Get all CSV files and extract indices from filenames
csv_files = glob.glob('*.csv')
angle_step = 360 / 16  # 22.5 degrees

# Dictionary to store angle and mean value pairs
data = {}

# Read each CSV file
for csv_file in csv_files:
    # Extract index from filename (e.g., '0.csv' -> 0)
    index = int(os.path.splitext(csv_file)[0])

    # Calculate angle in degrees
    angle = index * angle_step

    # Read CSV and calculate mean of the Value column
    df = pd.read_csv(csv_file)

    # Apply specific transformations based on file index
    if index == 6:
        # For file 6: negate all data above 0
        df.loc[df['Value'] > 0, 'Value'] = -df.loc[df['Value'] > 0, 'Value']
    elif index in [13, 14]:
        # For files 13 and 14: make negative numbers positive
        df.loc[df['Value'] < 0, 'Value'] = -df.loc[df['Value'] < 0, 'Value']

    mean_value = df['Value'].mean()

    data[angle] = mean_value

# Sort by angle
angles = np.array(sorted(data.keys()))
values = np.array([data[angle] for angle in angles])

# Convert angles to radians for polar plot
angles_rad = np.deg2rad(angles)

# Close the plot by adding the first point at the end
angles_rad = np.append(angles_rad, angles_rad[0])
values = np.append(values, values[0])

# Create polar plot
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='polar')

# Plot the radiation pattern
ax.plot(angles_rad, values, 'b-', linewidth=2, marker='o', markersize=8)
ax.fill(angles_rad, values, alpha=0.25)

# Set the direction of 0 degrees to the top (North)
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)  # Clockwise

# Add labels
ax.set_title('Antenna Radiation Pattern\n(Mean Values vs Angle)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Angle (degrees)', fontsize=12)
ax.grid(True)

# Add radial labels
ax.set_rlabel_position(45)

plt.tight_layout()
plt.savefig('radiation_pattern.png', dpi=300, bbox_inches='tight')
print(f"Plot saved as 'radiation_pattern.png'")
print(f"\nStatistics:")
print(f"Number of angles: {len(angles)}")
print(f"Angular step: {angle_step} degrees")
print(f"Mean value range: {values.min():.2f} - {values.max():.2f}")
print(f"Overall mean: {values.mean():.2f}")

plt.show()
