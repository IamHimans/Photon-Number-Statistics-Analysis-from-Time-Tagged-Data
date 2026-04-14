# Photon Number Statistics from Raw Time-Tagger Data

A Python tool for analyzing raw timestamped photon data from a Time-to-Digital Converter (TDC) or time tagger (e.g., quTAU). This script extracts the photon-number distribution $P(n)$ and calculates fundamental statistical metrics to characterize unheralded classical (and pseudo-thermal) light sources.

## Overview
In experimental quantum optics, distinguishing between coherent (laser) light, thermal (chaotic) light, and non-classical (quantum) light requires analyzing the statistical fluctuations in photon arrivals. 

This script reads raw timestamps, bins them into user-defined time intervals ($\Delta T$), and computes the empirical probability distribution of detecting $n$ photons per interval. It then compares this distribution against a theoretical Poissonian model and extracts the Fano Factor and Mandel's Q parameter.



## Physics Background
The nature of the light source is determined by the variance $\text{Var}(n)$ and the mean $\langle n \rangle$ of the photon counts per bin:

* **Fano Factor ($F$):** $$F = \frac{\text{Var}(n)}{\langle n \rangle}$$
* **Mandel's Q Parameter ($Q$):** $$Q = \frac{\text{Var}(n) - \langle n \rangle}{\langle n \rangle}$$

Based on the calculated $Q$ parameter, the script categorizes the light:
* **$Q = 0 \ (F = 1)$**: Poissonian statistics (Coherent light, e.g., an ideal laser).
* **$Q > 0 \ (F > 1)$**: Super-Poissonian statistics (Thermal/chaotic light, e.g., pseudo-thermal ground glass source).
* **$Q < 0 \ (F < 1)$**: Sub-Poissonian statistics (Non-classical light, e.g., single-photon sources).

## Prerequisites
The script requires Python 3 and the following standard scientific libraries:
* `numpy`
* `pandas`
* `matplotlib`
* `scipy`

## Data Format
The script expects a `.txt` or `.csv` file containing raw time-tagger outputs with at least two columns:
1. `timestamp`: The absolute arrival time of the photon (in hardware-specific ticks).
2. `channel`: The input channel of the time tagger (e.g., 1 or 2 corresponding to specific SPADs).

*Note: Large files (e.g., >100 MB) are handled efficiently using Pandas.*

## Usage
1. Clone the repository and place your data file in the same directory.
2. Open the script and modify the **User Settings** block:

```python
input_file = "Diode_timestamp=2min_25k_25k.txt"  # Your data file
target_channel = 1                           # SPAD channel to analyze
bin_duration_us = 1000                       # Integration time Delta T in microseconds
tick_resolution_ps = 81                      # Hardware resolution in picoseconds (quTAU = 81 ps)
