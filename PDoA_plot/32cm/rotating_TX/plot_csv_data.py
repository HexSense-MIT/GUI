import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# Get all CSV files in the current directory
csv_files = sorted(glob.glob('*.csv'), key=lambda x: int(os.path.splitext(x)[0]) if os.path.splitext(x)[0].isdigit() else float('inf'))

# Determine the number of subplots needed
n_files = len(csv_files)
if n_files == 0:
    print("No CSV files found in the current directory.")
    exit()

# Calculate grid dimensions (try to make it as square as possible)
n_cols = int(np.ceil(np.sqrt(n_files)))
n_rows = int(np.ceil(n_files / n_cols))

# Create the figure and subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
fig.suptitle('Data from CSV Files', fontsize=16, fontweight='bold')

# Flatten axes array for easier iteration
if n_files == 1:
    axes = [axes]
else:
    axes = axes.flatten()

# Plot each CSV file
for idx, csv_file in enumerate(csv_files):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Convert timestamp to datetime for better plotting
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            # Create a time offset in seconds from the first timestamp
            time_offset = (df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds()
            x_data = time_offset
            x_label = 'Time (seconds)'
        else:
            # If no timestamp, use index
            x_data = df.index
            x_label = 'Sample Index'

        # Plot the data
        if 'Value' in df.columns:
            axes[idx].plot(x_data, df['Value'], linewidth=1.5)
            axes[idx].set_ylabel('Value')
        else:
            # Plot all numeric columns
            for col in df.select_dtypes(include=[np.number]).columns:
                axes[idx].plot(x_data, df[col], label=col, linewidth=1.5)
            axes[idx].legend()

        axes[idx].set_xlabel(x_label)
        axes[idx].set_title(f'{os.path.basename(csv_file)}')
        axes[idx].grid(True, alpha=0.3)

    except Exception as e:
        axes[idx].text(0.5, 0.5, f'Error reading {csv_file}\n{str(e)}',
                      ha='center', va='center', transform=axes[idx].transAxes)
        axes[idx].set_title(f'{os.path.basename(csv_file)} (Error)')

# Hide any unused subplots
for idx in range(n_files, len(axes)):
    axes[idx].axis('off')

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the figure
output_file = 'all_plots.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"Plot saved as {output_file}")

# Display the plot
plt.show()
