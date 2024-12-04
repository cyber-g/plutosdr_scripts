#!/usr/bin/env python

# This python script is used to load and to generate some example signals.
# Signals are supposed to obtained with the download_modulated_signals.sh shell
# script. Signals are from IIO oscilloscope and are stored here in the signals/
# directory. 
# 
# - The script asks the user to enter the URI of the PlutoSDR.
# - The script parses the signals/ directory and asks the user to choose a
#   signal to load. (signals can be pre-discovered by using the utils_signals.py
#   script)
# - The signal is then loaded and plotted. 
# - The script then asks the user either to set a transmit TX Attenuation or to
#   perform a sweep of the TX Attenuation. 
# - The script also asks the user to choose if the signal is to be captured with
#   the RX of the Pluto and plotted (spectrum).
# - Then, the Pluto is configured to transmit the signal with the chosen TX
#   Attenuation.  

# Nov. 2024
# Germain PHAM

# Licensed under the GPL-2.

import os
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import adi
import time

N_LEV_DAC = (2**14)-1 # Number of levels of the DAC
# cf https://analogdevicesinc.github.io/pyadi-iio/buffers/index.html#cyclic-mode
# or https://github.com/analogdevicesinc/pyadi-iio/blob/main/examples/pluto.py

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
    mat_dat = np.loadtxt(signal_file, skiprows=1, dtype=int)
    # Convert to complex float
    signal = mat_dat[:,0] + 1j*mat_dat[:,1]

# normalize the signal to have a maximum amplitude of I or Q set to 1
signal = signal / np.max(np.abs([signal.real, signal.imag]))
# normalize the signal to have a maximum amplitude of I or Q set to N_LEV_DAC
signal = signal * N_LEV_DAC

# Ask user for the sampling frequency
fs = float(input("Enter the sampling frequency of the signal (MHz): "))
fs = fs * 1e6
# Ask user the RF bandwidth to set on the Pluto
rf_bandwidth = float(input("Enter the RF bandwidth to set on the Pluto (MHz): "))
rf_bandwidth = rf_bandwidth * 1e6

# # Plot the signal spectrum
# plt.figure()
# plt.psd(np.squeeze(signal), Fs=fs)
# plt.title("Signal spectrum")
# plt.show(block=False)

# Ask the user to set the TX attenuation or to perform a sweep
tx_attenuation_y_n = input("Do you want to set a TX attenuation gain (1) or perform a sweep (2)? ")
if tx_attenuation_y_n == "1":
    tx_gain_fixed = float(input("Enter the TX gain (dB) (should be a negative value): "))
    sweep = False
else:
    sweep = True

# Ask the user if the signal is to be captured with the RX of the Pluto
rx_capture = input("Do you want to capture the signal with the RX of the Pluto (y/n)? ")
if rx_capture == "y":
    rx_capture = True
else:
    rx_capture = False


# Connect to the PlutoSDR
sdr = adi.Pluto(uri=uri_str)

# Configure the PlutoSDR
# filter
# gain_control_mode_chan0
# loopback
# rx_hardwaregain_chan0
# rx_lo
# rx_rf_bandwidth
# sample_rate
# tx_hardwaregain_chan0
# tx_lo
# tx_rf_bandwidth
# tx_channel_names
# tx_cyclic_buffer
# tx_enabled_channels
# tx_destroy_buffer()

sdr.tx_destroy_buffer() # Stop any previous transmission

sdr.sample_rate = int(fs)
sdr.rx_rf_bandwidth = int(rf_bandwidth)
sdr.tx_rf_bandwidth = int(rf_bandwidth)
sdr.tx_lo = int(2.4e9)
sdr.rx_lo = int(2.4e9)
# TX Specific
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = -89
# RX Specific
sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = 0
sdr.rx_buffer_size = 2*len(signal) # Set the buffer size to 2 times the signal length

# If Fs == 61.44MSps, load the filter filters/61_44_28MHz.ftr
# If Fs == 30.72MSps, load the filter filters/LTE20_MHz.ftr
# if fs == 61.44e6:
#     sdr.filter = "filters/61_44_28MHz.ftr" 
# if fs == 30.72e6:
#     sdr.filter = "filters/LTE20_MHz.ftr"
# # This is disabled because the filter modifies significantly the signal

# Transmit the signal
sdr.tx(np.squeeze(signal))
if sweep:
    for tx_gain in range(-16, 0, 2):
        print(f"Transmitting signal with TX gain set to {tx_gain} dB")
        sdr.tx_hardwaregain_chan0 = tx_gain
        # wait for 2 seconds
        time.sleep(2)
        if rx_capture:
            data = sdr.rx()
            plt.figure()
            plt.psd(data, Fs=fs)
            plt.title(f"Received signal with TX gain set to {tx_gain} dB")
            plt.ylim(-78, -18)
            plt.show(block=False)
            time.sleep(0.5)
        else:
            input("Press Enter to continue...")
else:
    print(f"Transmitting signal with TX gain set to {tx_gain_fixed} dB")
    sdr.tx_hardwaregain_chan0 = tx_gain_fixed
    # wait for 2 seconds
    time.sleep(2)
    if rx_capture:
        data = sdr.rx()
        plt.figure()
        plt.psd(data, Fs=fs)
        plt.title(f"Received signal with TX gain set to {tx_gain_fixed} dB")
        plt.ylim(-78, -18)
        plt.show(block=False)
        time.sleep(0.5)
    else:
        input("Press Enter to continue...")
        

print("Length of the initial signal: ", len(signal))
if rx_capture:
    print("Length of the captured signal: ", len(data))

# Stop the transmission
sdr.tx_destroy_buffer()
print("Transmission terminated")


input("Press Enter to exit...")