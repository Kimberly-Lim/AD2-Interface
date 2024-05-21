
"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-28

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy 
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import os
import csv 


steps = 151
start = 1e2
stop = 1e6
reference = 1e3

# creation of directory
output_dir = "Impedance_Data_Collection"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Create the main window
root = tk.Tk()
root.title("Measurement Settings")

# Set the window size
root.geometry("600x400")
        
#How the impedance Anaylyzer actully works and makes Measurments
def makeMeasurement(steps, start, stop, reference, voltage, makeMeasureTime):
    #Capture Current Date
    current_date = datetime.now()
    nowY = current_date.year
    nowD = current_date.day
    nowM = current_date.month
    now = str(nowM)+ '-' + str(nowD)+ '-' + str(nowY)
    voltage = 1
    makeMeasureTime = 6

    #Capture Current Time
    t = time.localtime()
    current_time = time.strftime("%H-%M-%S", t)


    if sys.platform.startswith("win"):
        dwf = cdll.LoadLibrary("dwf.dll")
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")

    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))

    hdwf = c_int()
    szerr = create_string_buffer(512)
    print("Opening first device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        print("failed to open device")
        quit()

    # this option will enable dynamic adjustment of analog out settings like: frequency, amplitude...
    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3)) 

    sts = c_byte()


    print("Reference: "+str(reference)+" Ohm  Frequency: "+str(start)+" Hz ... "+str(stop/1e3)+" kHz for nanofarad capacitors")
    dwf.FDwfAnalogImpedanceReset(hdwf)
    dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
    dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference)) # reference resistor value in Ohms
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(start)) # frequency in Hertz
    dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1)) # 1V amplitude = 2V peak2peak signal
    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # start
    time.sleep(2)

    rgHz = [0.0]*steps
    rgRs = [0.0]*steps
    rgXs = [0.0]*steps
    rgPhase = [0.0]*steps

    for i in range(steps):
        hz = stop * pow(10.0, 1.0*(1.0*i/(steps-1)-1)*math.log10(stop/start)) # exponential frequency steps
        print("Step: "+str(i)+" "+str(hz)+"Hz")
        rgHz[i] = hz
        dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz)) # frequency in Hertz
        # if settle time is required for the DUT, wait and restart the acquisition
        # time.sleep(0.01) 
        # dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))
        while True:
            if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
                dwf.FDwfGetLastErrorMsg(szerr)
                print(str(szerr.value))
                quit()
            if sts.value == 2:
                break
        resistance = c_double()
        reactance = c_double()
        phase = c_double()

        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase , byref(phase))
        # add other measurements here (impedance, impedanceVReal impedanceVImag, impedancelreal, impedancelimag)
        

        rgRs[i] = abs(resistance.value) # absolute value for logarithmic plot
        rgXs[i] = abs(reactance.value)
        rgPhase[i] = (phase.value * 180)/3.14159265358979


        now_time = now + '_at_' + current_time + '_data'
        data = pd.DataFrame({
                             'Frequency(Hz)': rgHz,'Absolute Resistance(Ohm)': rgRs, 'Absolute Reactance(Ohm)': rgXs, 'Phase(degrees)': rgPhase})

        # Save the DataFrame to a CSV file
        csv_filename = os.path.join(output_dir, f"Impedance_Data_{now}_{current_time}.csv")
        data.to_csv(csv_filename, index=False)
        
        for iCh in range(2):
            warn = c_int()
            dwf.FDwfAnalogImpedanceStatusWarning(hdwf, c_int(iCh), byref(warn))
            if warn.value:
                dOff = c_double()
                dRng = c_double()
                dwf.FDwfAnalogInChannelOffsetGet(hdwf, c_int(iCh), byref(dOff))
                dwf.FDwfAnalogInChannelRangeGet(hdwf, c_int(iCh), byref(dRng))
                if warn.value & 1:
                    print("Out of range on Channel "+str(iCh+1)+" <= "+str(dOff.value - dRng.value/2)+"V")
                if warn.value & 2:
                    print("Out of range on Channel "+str(iCh+1)+" >= "+str(dOff.value + dRng.value/2)+"V")

    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # stop
    dwf.FDwfDeviceClose(hdwf)

    print(f"Data saved to {csv_filename}")

    ax = plt.gca()
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()

    
#Extracts Steps value from GUI
def update_steps(*args):
    global steps_int
    try:

        # Convert the entry to an integer
        steps_int = int(steps.get())

        print("Updated Steps to:", steps_int)

    except ValueError:

        print("Invalid input for steps. Please enter an integer.")

        steps.set("151")  # Reset to default if invalid

#Extracts Start value from GUI
def update_start(*args):
    global start_int
    try:

        # Convert the entry to an integer
        start_int = int(startF.get())

        print("Updated Start to:", start_int)

    except ValueError:

        print("Invalid input for start. Please enter an integer.")

        startF.set("100")  # Reset to default if invalid

#Extracts Stop value from GUI
def update_stop(*args):
    global stop_int
    try:

        # Convert the entry to an integer
        stop_int = int(stopF.get())

        print("Updated Stop to:", stop_int)

    except ValueError:

        print("Invalid input for start. Please enter an integer.")

        stopF.set("15000000")  # Reset to default if invalid

# Function to update amplitude
def update_amplitude(*args):
    global amplitude 
    amplitude = amplitude_var.get()
    amplitude_values = {
        "2 V" : 2,
        "1 V" : 1,
        "500 mV" : 0.5,
        "200 mV" : 0.2,
        "100 mV" : 0.1,
        "50 mV" : 0.05,
        "20 mV" : 0.02,
        "10 mV" : 0.01,
        "5 mV" : 0.005,
        "0 V" : 0
    }

# Function to update reference resistance
def update_resistance(*args):
    global reference
    resistance_values = {
        "1 MΩ": 1e6,
        "100 kΩ": 1e5,
        "10 kΩ": 1e4,
        "1 kΩ": 1e3,
        "100 Ω": 100,
        "10 Ω": 10
    }
    reference = resistance_values.get(resistance_var.get(), 1e3)

# Function to start the measurement
def measure():
    # Update global variables with the selected values
    update_start()
    update_stop()
    update_amplitude()
    update_resistance()
    measure_interval = float(measure_interval_entry.get())
    # Call the function to make the measurement
    makeMeasurement(int(steps.get()), start, stop, reference, amplitude, measure_interval)

# def measure():
#     makeMeasurement(
#         int(steps.get()), int(startF.get()), int(stopF.get()), update_amplitude(), update_resistance())

# Function to handle Start and Stop
def staart():
    print("Measurement started")
    

def stoop():
    print("Measurement stopped")
    print("steps.get")

    

# Steps entry
tk.Label(root, text="Steps").grid(row=0, column=0)
steps = tk.StringVar(value="151")  # Default value
steps.trace_add("write", update_steps)  # Trace changes
steps_entry = ttk.Entry(root, textvariable=steps)
steps_entry.grid(row=1, column=0)


# Start Frequency entry
tk.Label(root, text="Start Freq(Hz)").grid(row=0, column=1)
startF = tk.StringVar(value="100")  # Default value
startF.trace_add("write", update_start)  # Trace changes
start_freq_entry = ttk.Entry(root, textvariable=startF)
start_freq_entry.grid(row=1, column=1)

# Stop Frequency entry
tk.Label(root, text="Stop Freq(Hz)").grid(row=0, column=2)
stopF = tk.StringVar(value="15000000")  # Default value
stopF.trace_add("write", update_stop)  # Trace changes
stop_freq_entry = ttk.Entry(root, textvariable=stopF)
stop_freq_entry.grid(row=1, column=2)


# Amplitude dropdown
tk.Label(root, text="Amplitude").grid(row=2, column=0)
amplitude_var = tk.StringVar()
amplitude_dropdown = ttk.Combobox(root, textvariable=amplitude_var, values=["2 V", "1 V", "500 mV", "200 mV", "100 mV", "50 mV", "20 mV", "10 mV", "5 mV", "0 V"])
amplitude_dropdown.grid(row=3, column=0)
amplitude_dropdown.current(0)  # Default selection

# Reference resistance dropdown
tk.Label(root, text="Reference resistance").grid(row=2, column=1)
resistance_var = tk.StringVar()
resistance_dropdown = ttk.Combobox(root, textvariable=resistance_var, values=["1 MΩ", "100 kΩ", "10 kΩ", "1 kΩ", "100 Ω", "10 Ω"])
resistance_dropdown.grid(row=3, column=1)
resistance_dropdown.current(3)  # Default selection

# Measurement interval entry
tk.Label(root, text="Measure once every _ hours").grid(row=2, column=2)
measure_interval_entry = ttk.Entry(root)
measure_interval_entry.grid(row=3, column=2)
measure_interval_entry.insert(0, "4")  # Default value

# Start and Stop buttons
start_button = tk.Button(root, text="Start", bg="green", command=measure)
start_button.grid(row=4, column=0)
stop_button = tk.Button(root, text="Stop", bg="red", command=stoop)
stop_button.grid(row=4, column=1)

# Run the application
root.mainloop()

plt.plot(rgHz, rgRs, rgHz, rgXs)
ax = plt.gca()
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()
