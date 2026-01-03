import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Get all CSV files and extract indices from filenames
csv_files = glob.glob('*.csv')
angle_step = 360 / 16  # 22.5 degrees

# Dictionary to store angle, mean, and std values
data = {}

# Read each CSV file
for csv_file in csv_files:
    # Extract index from filename (e.g., '0.csv' -> 0)
    index = int(os.path.splitext(csv_file)[0])

    # Calculate angle in degrees
    angle = index * angle_step

    # Read CSV
    df = pd.read_csv(csv_file)

    # Apply specific transformations based on file index
    # Apply specific transformations based on file index
    if index in [3, 6, 11]:
        df.loc[df['Value'] < 0, 'Value'] = -df.loc[df['Value'] < 0, 'Value']
    elif index == 12:
        df.loc[df['Value'] > 0, 'Value'] = -df.loc[df['Value'] > 0, 'Value']

    # Calculate mean and standard deviation
    mean_value = df['Value'].mean()
    std_value = df['Value'].std()

    data[angle] = {'mean': mean_value, 'std': std_value}

# Sort by angle
angles = np.array(sorted(data.keys()))
means = np.array([data[angle]['mean'] for angle in angles])
stds = np.array([data[angle]['std'] for angle in angles])

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot mean values with error bars
ax.errorbar(angles, means, yerr=stds,
            fmt='o-', linewidth=2, markersize=8,
            capsize=5, capthick=2,
            label='Mean ± Std Dev')

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Labels and title
ax.set_xlabel('Angle (degrees)', fontsize=12, fontweight='bold')
ax.set_ylabel('Measurement Value', fontsize=12, fontweight='bold')
ax.set_title('Mean Measurements vs Angle with Error Bars',
             fontsize=14, fontweight='bold')

# Set x-axis ticks to show all angles
ax.set_xticks(angles)
ax.set_xticklabels([f'{int(a)}°' for a in angles], rotation=45, ha='right')

# Add legend
ax.legend(fontsize=10)

# Adjust layout
plt.tight_layout()

# Save the figure
output_file = 'mean_with_error_bars.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Plot saved as '{output_file}'")

# Print statistics
print(f"\nStatistics:")
print(f"Number of angles: {len(angles)}")
print(f"Angular step: {angle_step} degrees")
print(f"Mean value range: {means.min():.2f} - {means.max():.2f}")
print(f"Overall mean: {means.mean():.2f}")
print(f"Mean of std deviations: {stds.mean():.2f}")

# Display the plot
plt.show()
