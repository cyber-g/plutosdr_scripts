#!/usr/bin/env python

# This python script is used to load and to generate some example signals. 
# Signals are supposed to obtained with the download_modulated_signals.sh shell script. 
# Signals are from IIO oscilloscope and are stored here in the signals/ directory. 
# 
# Signals are supposed to be .mat files or .txt files (2 columns IQ samples, as integers).
#
# - The script asks the user to enter the URI of the PlutoSDR.
# - The script parses the signals/ directory and asks the user to choose a
#   signal to load. 
# - The signal is then loaded and plotted. Several characteristics of the signal
#   are displayed (e.g. sampling frequency, number of samples, PAPR, etc.)

# Nov. 2024
# Germain PHAM

# Licensed under the GPL-2.

import os
import scipy.io
import numpy as np
import matplotlib.pyplot as plt

# check if the file uri.local.env exists (excluded from git on purpose)
# if yes, read the uri from the file
# if not, ask the user to enter the uri, then save it in the file
try:
    with open('uri.local.env', 'r') as file:
        uri_str = file.read().replace('\n', '')
except:
    # Query the PlutoSDR URI to the user
    print("Please enter the URI of your PlutoSDR ")
    uri_str = input("(e.g. ip:192.168.2.1 or usb:1.5.5): ")
    with open('uri.local.env', 'w') as file:
        file.write(uri_str)

# Path of the directory where signal files are stored
signals_dir = "signals/"

# Parse the signals directory
signals = os.listdir(signals_dir)

# Display the list of signals
print("List of available signals:")
for i, signal in enumerate(signals):
    print(f"{i}: {signal}")

# Ask the user to choose a signal
signal_idx = int(input("Enter the index of the signal to load: "))
signal_file = signals_dir + signals[signal_idx]

# Load the signal
if signal_file.endswith(".mat"):
    # Load a .mat file
    mat_dat = scipy.io.loadmat(signal_file)
    signal = mat_dat['new']
else:
    # Load a .txt file, remove the first line (header), 2 columns integers
    signal = np.loadtxt(signal_file, skiprows=1, dtype=int)
    # Convert to complex float
    signal = signal[:,0] + 1j*signal[:,1]

# Ask user for the sampling frequency
fs = float(input("Enter the sampling frequency of the signal: "))

# Display the signal characteristics
print("") # Empty line
print(f"Signal loaded from {signal_file}")
print(f"Signal characteristics:")
print(f"Average power: {np.mean(np.abs(signal)**2)}")
print(f"Peak-to-average power ratio: {np.max(np.abs(signal)**2)/np.mean(np.abs(signal)**2)}")
print(f"Peak-to-average power ratio (dB): {10*np.log10(np.max(np.abs(signal)**2)/np.mean(np.abs(signal)**2))}")
print(f"Number of samples: {len(signal)}")
print(f"Sampling frequency (User): {fs} Hz")

# Plot the signal spectrum
plt.figure()
plt.psd(np.squeeze(signal), Fs=fs)
plt.title("Signal spectrum")
plt.show()

