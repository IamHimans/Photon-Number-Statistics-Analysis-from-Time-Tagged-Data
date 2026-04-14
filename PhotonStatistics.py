import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==================================
# User settings (EDIT HERE)
# ==================================
input_file = "Diode_timestamp=2min_25k_25k.txt"      # Your timestamp file (should contain columns: timestamp, channel)
target_channel = 1           # The channel you want to analyze (e.g., SPCM channel)
max_rows = None              # Maximum rows to read (set None to read all 160MB)

# Binning Settings for Statistics
# This is the crucial parameter: The time interval (Delta T) over which to count photons.
# It should be much larger than the coherence time of the source.
bin_duration_us = 1000       # Photon counting time interval (Delta T) in microseconds (e.g., 1000 µs = 1 ms)

# Physical Constants
tick_resolution_ps = 81      # quTAU tick resolution in ps (~81 ps)
out_prefix = "photon_stats"  # Output prefix for plots and csv

# ==================================
# Data Loading and Preparation
# ==================================

print("Loading data...")
try:
    # Assuming two columns: timestamp and channel
    df = pd.read_csv(input_file, nrows=max_rows, header=None, names=["timestamp", "channel"])
except FileNotFoundError:
    print(f"Error: File not found at {input_file}")
    exit()

# Select data for the target channel
timestamps_ticks = df.loc[df["channel"] == target_channel, "timestamp"].values.astype(np.int64)

N_events = len(timestamps_ticks)
print(f"Loaded {N_events} events on channel {target_channel}")

if N_events == 0:
    print("Error: No data on the target channel.")
    exit()

# ----------------------------------
# Convert Time Settings
# ----------------------------------
# Total measurement time T (in ticks)
T_total_ticks = timestamps_ticks.max() - timestamps_ticks.min()
T_total_s = T_total_ticks * tick_resolution_ps / 1e12

# Convert the desired bin duration (Delta T) into clock ticks
tick_resolution_us = tick_resolution_ps / 1e6 # ps -> us
bin_duration_ticks = int(round(bin_duration_us / tick_resolution_us))
num_bins = int(T_total_ticks / bin_duration_ticks)

print(f"Total measurement time: {T_total_s:.2f} s")
print(f"Count interval (Delta T): {bin_duration_us} µs")
print(f"Total number of intervals: {num_bins}")

# ==================================
# Photon Counting and Statistics
# ==================================

# 1. Create Bins
# Define the edges of the counting intervals (from start to end of measurement)
start_time = timestamps_ticks.min()
end_time = start_time + num_bins * bin_duration_ticks
bin_edges = np.arange(start_time, end_time + 1, bin_duration_ticks)

# 2. Count Photons in each Bin
# This is a standard NumPy histogram calculation: it counts how many timestamps 
# fall into each interval defined by bin_edges.
# n_i = number of photons in the i-th interval
n_counts = np.histogram(timestamps_ticks, bins=bin_edges)[0]

# 3. Calculate Mean and Variance
# Average number of photons per interval: <n>
mean_n = np.mean(n_counts)
# Variance of the number of photons per interval: Var(n)
var_n = np.var(n_counts, ddof=1) # ddof=1 for sample variance

# 4. Calculate Q Parameter and Fano Factor
# Mandel's Q Parameter
Q_parameter = (var_n - mean_n) / mean_n

# Fano Factor
Fano_factor = var_n / mean_n

print("\n--- Calculated Photon Statistics ---")
print(f"Average counts per interval (<n>): {mean_n:.2f}")
print(f"Variance of counts (Var(n)): {var_n:.2f}")
print(f"Mandel's Q Parameter: {Q_parameter:.4f}")
print(f"Fano Factor (F): {Fano_factor:.4f}")

# Interpretation:
if np.isclose(Q_parameter, 0, atol=0.05):
    print("Interpretation: The source shows **Poissonian statistics** (coherent light).")
elif Q_parameter < 0:
    print("Interpretation: The source shows **sub-Poissonian statistics** (non-classical light/antibunching).")
else: # Q_parameter > 0
    print("Interpretation: The source shows **super-Poissonian statistics** (thermal/chaotic light).")

# ==================================
# Plotting the Photon-Number Distribution
# ==================================

# Count the frequency of each photon number (P(n))
unique_n, counts = np.unique(n_counts, return_counts=True)
prob_n = counts / num_bins # Probability P(n)

# Create an array of possible Poissonian probabilities for comparison
from scipy.stats import poisson
poisson_prob = poisson.pmf(unique_n, mu=mean_n)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 14
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.2
plt.figure(figsize=(8,5))
# Plot the measured distribution P(n)
plt.bar(unique_n, prob_n, width=0.9, color='skyblue', edgecolor='darkblue', alpha=0.7, label='Measured $P(n)$')
# Plot the theoretical Poissonian distribution for comparison
plt.plot(unique_n, poisson_prob, 'ro-', label=f'Poissonian ($\\langle n \\rangle={mean_n:.2f}$)')

plt.title('Photon-Number Distribution $P(n)$')
plt.xlabel('Number of Photons per Interval ($n$)')
plt.ylabel('Probability $P(n)$')
plt.text(0.95, 0.95, f'$Q = {Q_parameter:.3f}$\n$F = {Fano_factor:.3f}$',
         transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8))
plt.grid(axis='y', linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig(f"{out_prefix}_distribution.png", dpi=300)
plt.show()
print(f"Plot saved to {out_prefix}_distribution.png")