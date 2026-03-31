import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
from scipy.optimize import curve_fit

# Get all CSV files in the current directory
csv_files = sorted(glob.glob('*.csv'), key=lambda x: int(x.split('.')[0]))

# Read and process all CSV files
all_data = []
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        angle = int(csv_file.split('.')[0])

        # Calculate mean and std for PDoA
        pdoa_mean = df['PDoA'].mean()
        pdoa_std = df['PDoA'].std()

        # Calculate mean and std for AoA
        aoa_mean = df['AoA'].mean()
        aoa_std = df['AoA'].std()

        all_data.append({
            'angle': angle * 22.5,  # Convert filename to degrees
            'pdoa_mean': pdoa_mean,
            'pdoa_std': pdoa_std,
            'aoa_mean': aoa_mean,
            'aoa_std': aoa_std
        })
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")

# Convert to DataFrame
results_df = pd.DataFrame(all_data)
results_df = results_df.sort_values('angle')

# Filter data for linear regression (only -90 to 90 degrees)
regression_df_linear = results_df[(results_df['angle'] >= -90) & (results_df['angle'] <= 90)].copy()

# Filter data for sine regression (full range -180 to 180 degrees)
regression_df_sine = results_df[(results_df['angle'] >= -180) & (results_df['angle'] <= 180)].copy()

# Define sine function for curve fitting
def sine_function(x, amplitude, phase, offset):
    return amplitude * np.sin(np.radians(x) + phase) + offset

# Perform sine curve fitting on the full range
if len(regression_df_sine) > 0:
    try:
        # Initial guess for parameters
        initial_guess = [10, 0, 0]  # amplitude, phase, offset
        popt_sine, pcov = curve_fit(sine_function, regression_df_sine['angle'],
                                    regression_df_sine['pdoa_mean'], p0=initial_guess)

        # Generate smooth curve for plotting (-180 to 180)
        angle_fit_sine = np.linspace(-180, 180, 400)
        pdoa_fit_sine = sine_function(angle_fit_sine, *popt_sine)

        print(f"\nSine Regression Parameters:")
        print(f"Amplitude: {popt_sine[0]:.3f}")
        print(f"Phase: {popt_sine[1]:.3f} radians ({np.degrees(popt_sine[1]):.3f} degrees)")
        print(f"Offset: {popt_sine[2]:.3f}")

        has_sine_regression = True
    except Exception as e:
        print(f"Sine regression failed: {e}")
        has_sine_regression = False
else:
    has_sine_regression = False

# Perform linear regression on the filtered data (-90 to 90)
if len(regression_df_linear) > 0:
    try:
        # Linear fit: y = slope * x + intercept
        coeffs = np.polyfit(regression_df_linear['angle'], regression_df_linear['pdoa_mean'], 1)
        slope, intercept = coeffs

        # Generate line for plotting (-90 to 90)
        angle_fit_linear = np.linspace(-90, 90, 200)
        pdoa_fit_linear = slope * angle_fit_linear + intercept

        print(f"\nLinear Regression Parameters:")
        print(f"Slope: {slope:.3f}")
        print(f"Intercept: {intercept:.3f}")

        has_linear_regression = True
    except Exception as e:
        print(f"Linear regression failed: {e}")
        has_linear_regression = False
else:
    has_linear_regression = False

# Perform polynomial regression (3rd degree) on full range
# This provides a flexible fit that can capture non-linear patterns
if len(regression_df_sine) > 0:
    try:
        # Polynomial fit: y = a*x^3 + b*x^2 + c*x + d
        poly_coeffs = np.polyfit(regression_df_sine['angle'], regression_df_sine['pdoa_mean'], 3)

        # Generate curve for plotting (-180 to 180)
        angle_fit_poly = np.linspace(-180, 180, 400)
        pdoa_fit_poly = np.polyval(poly_coeffs, angle_fit_poly)

        # Calculate R-squared for goodness of fit
        pdoa_predicted = np.polyval(poly_coeffs, regression_df_sine['angle'])
        ss_res = np.sum((regression_df_sine['pdoa_mean'] - pdoa_predicted) ** 2)
        ss_tot = np.sum((regression_df_sine['pdoa_mean'] - regression_df_sine['pdoa_mean'].mean()) ** 2)
        r_squared_poly = 1 - (ss_res / ss_tot)

        print(f"\nPolynomial Regression (degree 3) Parameters:")
        print(f"Coefficients: {poly_coeffs}")
        print(f"R-squared: {r_squared_poly:.4f}")

        has_poly_regression = True
    except Exception as e:
        print(f"Polynomial regression failed: {e}")
        has_poly_regression = False
else:
    has_poly_regression = False

# Create Figure 1: PDoA Mean and Error
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.errorbar(results_df['angle'], results_df['pdoa_mean'],
             yerr=results_df['pdoa_std'],
             fmt='o-', capsize=5, capthick=2,
             markersize=8, linewidth=2, label='Measured Data')

# Plot regression curves if available
if has_sine_regression:
    ax1.plot(angle_fit_sine, pdoa_fit_sine, 'r--', linewidth=2.5,
             label=f'Sine Fit: {popt_sine[0]:.2f}·sin(x + {popt_sine[1]:.2f}) + {popt_sine[2]:.2f}')

if has_linear_regression:
    ax1.plot(angle_fit_linear, pdoa_fit_linear, 'g--', linewidth=2.5,
             label=f'Linear Fit: {slope:.2f}·x + {intercept:.2f}')

if has_poly_regression:
    ax1.plot(angle_fit_poly, pdoa_fit_poly, 'm--', linewidth=2.5,
             label=f'Poly Fit (deg 3, R²={r_squared_poly:.3f})')

ax1.set_xlabel('Angle (degrees)', fontsize=12)
ax1.set_ylabel('PDoA Mean', fontsize=12)
ax1.set_title('PDoA Mean and Standard Deviation vs Angle', fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax1.legend(fontsize=10)
ax1.set_xlim(-180, 180)

# Create Figure 2: AoA Mean and Error
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.errorbar(results_df['angle'], results_df['aoa_mean'],
             yerr=results_df['aoa_std'],
             fmt='s-', capsize=5, capthick=2,
             markersize=8, linewidth=2, color='orange')
ax2.set_xlabel('Angle (degrees)', fontsize=12)
ax2.set_ylabel('AoA Mean', fontsize=12)
ax2.set_title('AoA Mean and Standard Deviation vs Angle', fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# Print summary statistics
print("\nSummary Statistics:")
print(results_df.to_string(index=False))
