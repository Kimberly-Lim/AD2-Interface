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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import os
import csv 
import threading
from tkinter import messagebox
import time

# creation of directory
output_dir = "Impedance_Data_Collection"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

measurements_running = False
        
#How the impedance Anaylyzer actully works and makes Measurments
def makeMeasurement(steps, startFrequency, stopFrequency, reference, amplitude):
    #Capture Current Date
    current_date = datetime.now()
    nowY = current_date.year
    nowD = current_date.day
    nowM = current_date.month
    now = str(nowM)+ '-' + str(nowD)+ '-' + str(nowY)

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
    print("Opening first device\n")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        print("failed to open device")
        quit()

    # this option will enable dynamic adjustment of analog out settings like: frequency, amplitude...
    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3)) 

    sts = c_byte()

    # print("Reference: "+str(reference)+" Ohm  Frequency: "+str(startFrequency)+" Hz ... "+str(stopFrequency/1e3)+" kHz for nanofarad capacitors")
    dwf.FDwfAnalogImpedanceReset(hdwf)
    dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
    dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference)) # reference resistor value in Ohms
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(start_numeric_value)) # frequency in Hertz
    dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(amplitude)) # 1V amplitude = 2V peak2peak signal
    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # start
    time.sleep(2)

    rgHz = [0.0]*steps
    rgRs = [0.0]*steps
    rgXs = [0.0]*steps
    rgPhase = [0.0]*steps
    rgZ = [0.0]*steps
    rgRv = [0.0]*steps # real voltage
    rgIv = [0.0]*steps # imag voltage
    rgRc = [0.0]*steps # real current
    rgIc = [0.0]*steps # imag current

    for i in range(steps):
        hz = stop_numeric_value * pow(10.0, 1.0*(1.0*i/(steps-1)-1)*math.log10(stop_numeric_value/start_numeric_value)) # exponential frequency steps
        # log_label =tk.Label(frame_settings, text=f"Step: {i + 1} Frequency: {hz:.2f} Hz")
        log_label =tk.Label(frame_settings, text=f"Step Count Progress: {i + 1}")
        log_label.grid(row=5, column=0, padx=5, pady=5, sticky='NW')
        root.update()

        # Update the step count label on the GUI thread
        total_steps = int(steps_entry.get())

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
        impedance = c_double()
        realVoltage = c_double()
        imagVoltage = c_double()
        realCurrent = c_double()
        imagCurrent = c_double()

        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase , byref(phase))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceVreal, byref(realVoltage))      
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceVimag, byref(imagVoltage)) 
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceIreal, byref(realCurrent))      
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceIimag, byref(imagCurrent))                
        # add other measurements here (impedance, impedanceVReal impedanceVImag, impedancelreal, impedancelimag)

        rgRs[i] = abs(resistance.value) # absolute value for logarithmic plot
        rgXs[i] = abs(reactance.value)
        rgPhase[i] = (phase.value * 180)/3.14159265358979
        rgZ[i] = abs(impedance.value)
        rgRv[i] = abs(realVoltage.value)
        rgIv[i] = abs(imagVoltage.value)
        rgRc[i] = abs(realCurrent.value)
        rgIc[i] = abs(imagCurrent.value)

        now_time = now + '_at_' + current_time + '_data'

        data = pd.DataFrame({
                             'Frequency(Hz)': rgHz,'Impedance(Ohm)' : rgZ, 'Absolute Resistance(Ohm)': rgRs, 
                             'Absolute Reactance(Ohm)': rgXs, 'Phase(degrees)': rgPhase, 'Real Voltage(volts)': rgRv, 'Imaginary Voltage(volts)': rgIv, 
                              'Real Current(amps)': rgRc, 'Imaginary Current(amps)': rgIc })

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

    # Create the impedance graph
    fig1, ax1 = plt.subplots(figsize=(2,1))
    fig1.suptitle('Impedance', fontsize = 8)
    ax1.plot(rgHz, rgZ, linewidth='1')
    plt.xscale("log")
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    plt.xlabel("Frequency (Hz)", fontsize = 5)
    plt.ylabel("Magnitude(Ohms)", fontsize = 5)
    canvas1 = FigureCanvasTkAgg(fig1, master=frame_graphs)
    fig1.patch.set_alpha(0.0)  # Make the figure background transparent
    ax1.patch.set_alpha(0.0)   # Make the axes background transparent
    canvas1.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
    canvas1.draw()
    canvas1.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

    # Toolbar for impedance graph
    ttk.Label(frame_settings, text="Impedance ToolBar: ").grid(row=4, column=1, padx=1, pady=1, sticky='e')
    toolbar_frame1 = tk.Frame(frame_settings)
    toolbar_frame1.grid(row=4, column=2, padx=1, pady=1, sticky='e')
    toolbar1 = NavigationToolbar2Tk(canvas1, toolbar_frame1)

    # Create the phase angle graph
    fig1, ax2 = plt.subplots(figsize=(2,1))
    fig1.suptitle('Phase Angle', fontsize=8)
    fig1.patch.set_alpha(0.0)  # Make the figure background transparent
    ax2.patch.set_alpha(0.0)   # Make the axes background transparent
    ax2.plot(rgHz, rgPhase, linewidth='1')
    plt.xscale("log")
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    canvas2 = FigureCanvasTkAgg(fig1, master=frame_graphs)
    plt.xlabel("Frequency (Hz)", fontsize = 5)
    plt.ylabel("Phase (degrees)", fontsize = 5)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
    canvas2.get_tk_widget().configure(bg=default_bg_color)  # Match the background color

    # Toolbar for phase angle graph
    ttk.Label(frame_settings, text="Phase Angle ToolBar: ").grid(row=5, column=1, padx=1, pady=1, sticky='e')    
    toolbar_frame2 = tk.Frame(frame_settings)
    toolbar_frame2.grid(row=5, column=2, padx=1, pady=1, sticky='e')
    toolbar2 = NavigationToolbar2Tk(canvas2, toolbar_frame2)

    # Create the nyquist graph
    fig1, ax3 = plt.subplots(figsize=(2,1))
    ax3.plot(rgRs, rgXs, linewidth='1')
    fig1.suptitle('Nyquist', fontsize= 8)
    fig1.patch.set_alpha(0.0)  # Make the figure background transparent
    ax3.patch.set_alpha(0.0)   # Make the axes background transparent
    canvas3 = FigureCanvasTkAgg(fig1, master=frame_graphs)
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=3)
    plt.xlabel("Resistance (Ohms)", fontsize = 5)
    plt.ylabel("-Reactance (Ohms)", fontsize = 5)
    canvas3.draw()
    canvas3.get_tk_widget().grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky='nsew')
    canvas3.get_tk_widget().configure(bg=default_bg_color)  # Match the background color

    # tool bar functionality for Nyquist graph
    ttk.Label(frame_settings, text="Nyquist ToolBar: ").grid(row=6, column=1, padx=1, pady=1, sticky='e')    
    toolbar_frame3 = tk.Frame(frame_settings)
    toolbar_frame3.grid(row=6, column=2, padx=1, pady=1, sticky='e')
    toolbar3 = NavigationToolbar2Tk(canvas3, toolbar_frame3)
    
# end of def makeMeasurement 

#Extracts Steps value from GUI
def update_steps(*args):
    global steps_int
    try:
        # Convert the entry to an integer
        steps_int = int(steps.get())
        if steps_int < 0:
            # raise ValueError("Steps cannot be negative.")
            messagebox.showerror('Invalid Input', 'Steps must be a positive integer')
            print("Updated Steps to:", steps_int)

    except ValueError as e:
        print("Invalid input for steps. Please enter a positive integer")

# Dictionary for frequency values
frequency_dict = {
    "1 Hz": 1,
    "10 Hz": 10,
    "100 Hz": 100,
    "1 kHz": 1000,
    "10 kHz": 10000,
    "100 kHz": 100000,
    "1 MHz": 1000000,
    "10 MHz": 10000000,
    "15 MHz": 15000000
}

startFrequency = None
stopFrequency = None 
amplitude = None
reference = None

def on_select_start(event):
    global startFrequency
    global start_numeric_value
    startFrequency = startF_dropdown.get()
    start_numeric_value = frequency_dict[startFrequency]
    print(f"Selected: {startFrequency}, Numeric Value: {start_numeric_value}")

    return start_numeric_value

# Function to handle selection for stop frequency
def on_select_stop(event):
    global stopFrequency
    global stop_numeric_value
    stopFrequency = stopF_dropdown.get()
    stop_numeric_value = frequency_dict[stopFrequency]
    print(f"Selected: {stopFrequency}, Numeric Value: {stop_numeric_value}")

    return stop_numeric_value

# Dictionary for amplitude values
amplitude_dict = {
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

# Function to handle selection for amplitude
def on_select_amp(event):
    global amplitude
    global amplitude_numeric_value
    amplitude = amplitude_dropdown.get()
    amplitude_numeric_value = amplitude_dict[amplitude]
    print(f"Selected: {amplitude}, Numeric Value: {amplitude_numeric_value}")

    return amplitude_numeric_value

# Dictionary for resistance values
reference_dict = {
    "1 MΩ" : 1000000,
    "100 kΩ" : 100000,
    "10 kΩ" : 10000,
    "1 kΩ" : 1000,
    "100 Ω" : 100,
    "10 Ω" : 10
}

# Function to handle selection for resistance
def on_select_res(event):
    global reference
    global reference_numeric_value
    reference = resistance_dropdown.get()
    reference_numeric_value = reference_dict[reference]
    print(f"Selected: {reference}, Numeric Value: {reference_numeric_value}")

    return reference_numeric_value

# Function to start the measurement
def measure():
    global startFrequency, stopFrequency, amplitude, reference
    # Update global variables with the selected values
    steps = int(steps_entry.get())
    startFrequency = on_select_start(startFrequency)
    stopFrequency = on_select_stop(stopFrequency)
    reference = on_select_res(reference)
    amplitude = on_select_amp(amplitude)
    # Call the function to make the measurement
    threading.Thread(target=makeMeasurement(steps, startFrequency, stopFrequency, reference, amplitude)).start()

# Create the main window
root = tk.Tk()
fig, ax = plt.subplots()
root.title("Measurement Settings")
default_bg_color = root.cget('bg')

# Set the window size
root.geometry("1200x600")

# Create a frame for the settings
frame_settings = tk.Frame(root, bg='white')
frame_settings.grid(row=0, column=0, rowspan=2, columnspan=3, padx=10, pady=10, sticky='nsew')

# Function to get user input and call_repeatedly
def start_repeating():
    try:
        interval = int(measure_interval_entry.get())
        if interval <= 0:
            raise ValueError("Interval must be positive")
        interval_ms = interval * 60 * 1000
        call_repeatedly(interval_ms)    
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

# Function to repeatedly call desired function
def call_repeatedly(interval_ms):
    global job
    measure()
    start_countdown(interval_ms // 1000)
    job = root.after(interval_ms, lambda: call_repeatedly(interval_ms))
# Function to stop the interval calling
def stop_repeating():
    global job, countdown_job
    if job:
        root.after_cancel(job)
        job = None
    if countdown_job:
        root.after_cancel(countdown_job)
        countdown_job = None
    countdown_label.config(text="00:00")
# Function to handle the countdown
def start_countdown(seconds):
    global countdown_job
    def update_countdown():
        nonlocal seconds
        minutes, secs = divmod(seconds, 60)
        countdown_label.config(text=f"Next call in: {minutes:02}:{secs:02}") 
        # countdown_label = tk.Label(frame_settings, text=f"Next call in: {minutes:02}:{secs:02}")       
        if seconds > 0:
            global countdown_job
            seconds -=1
            countdown_job = root.after(1000, update_countdown)
    update_countdown()

# Initialize global variables
countdown_label = tk.Label(frame_settings, text="00:00")
countdown_label.grid(row=8, column=2, padx=2, pady=2, sticky='NW')
root.update()
job = None
countdown_job = None

# Make the main window's grid layout adjustable
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=2)
root.rowconfigure(3, weight=2)

# Configure grid layout for frame_settings
frame_settings.columnconfigure(0, weight=1)
frame_settings.columnconfigure(1, weight=1)
frame_settings.columnconfigure(2, weight=1)
frame_settings.rowconfigure(0, weight=1)
frame_settings.rowconfigure(1, weight=1)
frame_settings.rowconfigure(2, weight=1)

# Create a frame for the graphs
frame_graphs = tk.Frame(root, bg=default_bg_color)
frame_graphs.grid(row=2, column=0, rowspan=2, columnspan=3, padx=10, pady=10, sticky='nsew')

# Make the frame expand with the window
frame_graphs.columnconfigure(0, weight=1)
frame_graphs.columnconfigure(1, weight=1)
frame_graphs.columnconfigure(2, weight=1)
frame_graphs.rowconfigure(0, weight=1)
frame_graphs.rowconfigure(1, weight=1)

# Make the main window's grid layout adjustable
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=2)
root.rowconfigure(3, weight=2)

# Create a frame for the settings
frame_settings = tk.Frame(root)
frame_settings.grid(row=0, column=0, rowspan=2, columnspan=3, padx=10, pady=10, sticky='nsew')

# Configure grid layout for frame_settings
frame_settings.columnconfigure(0, weight=1)
frame_settings.columnconfigure(1, weight=1)
frame_settings.columnconfigure(2, weight=1)
frame_settings.rowconfigure(0, weight=1)
frame_settings.rowconfigure(1, weight=1)
frame_settings.rowconfigure(2, weight=1)

# Add settings widgets to frame_settings
steps_label = tk.Label(frame_settings, text="Steps:")
steps_label.grid(row=0, column=0, padx=0, pady=0, sticky='NW')
steps_entry = tk.Entry(frame_settings)
steps_entry.insert(0, "151")  # Set default value to 151
steps_entry.grid(row=1, column=0, padx=0, pady=0, sticky='NW')

# Add Start Frequency entry to frame_settings
startF_label = tk.Label(frame_settings, text="Start Frequency")
startF_label.grid(row=0, column=1, padx=5, pady=5, sticky='NW')
startF_dropdown = ttk.Combobox(frame_settings, values=list(frequency_dict.keys()))
startF_dropdown.bind("<<ComboboxSelected>>", on_select_start)
startF_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky='NW')
startF_dropdown.current(list(frequency_dict.keys()).index("100 Hz"))  # Set default value to 100 Hz

# Add Stop Frequency entry to frame_settings
stopF_label = tk.Label(frame_settings, text="Stop Frequency")
stopF_label.grid(row=0, column=2, padx=5, pady=5, sticky='NW')
stopF_dropdown = ttk.Combobox(frame_settings, values=list(frequency_dict.keys()))
stopF_dropdown.bind("<<ComboboxSelected>>", on_select_start)
stopF_dropdown.grid(row=1, column=2, padx=5, pady=5, sticky='NW')
stopF_dropdown.current(list(frequency_dict.keys()).index("1 MHz"))  # Set default value to 100 Hz

# Add amplitude entry to frame_settings
amplitude_label = tk.Label(frame_settings, text="Amplitude")
amplitude_label.grid(row=2, column=0, padx=5, pady=5, sticky='NW')
amplitude_dropdown = ttk.Combobox(frame_settings, values=list(amplitude_dict.keys()))
amplitude_dropdown.bind("<<ComboboxSelected>>", on_select_amp)
amplitude_dropdown.grid(row=3, column=0, padx=5, pady=5, sticky='NW')
amplitude_dropdown.current(list(amplitude_dict.keys()).index("1 V"))  # Set default value to 100 Hz

# Add reference resistance entry to frame_settings
resistance_label = tk.Label(frame_settings, text="Reference Resistance")
resistance_label.grid(row=2, column=1, padx=5, pady=5, sticky='NW')
resistance_dropdown = ttk.Combobox(frame_settings, values=list(reference_dict.keys()))
resistance_dropdown.bind("<<ComboboxSelected>>", on_select_res)
resistance_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky='NW')
resistance_dropdown.current(list(reference_dict.keys()).index("1 kΩ"))  # Set default value to 100 Hz

# Add Measurement Interval entry to frame_settings
ttk.Label(frame_settings, text="Enter Interval In Minutes:").grid(row=2, column=2, padx=5, pady=5, sticky='NW')
measure_interval_entry = ttk.Entry(frame_settings)
measure_interval_entry.grid(row=3, column=2, padx=5, pady=5, sticky='NW')

# start button
start_button = ttk.Button(
    frame_settings,
    text='Start Measurement',
    # Call the function to make the measurement
    # command=threading.Thread(target=start_repeating).start
    command= start_repeating
)
start_button.grid(column=0, row=4, padx=10, pady=10, sticky='NW')

stop_button = ttk.Button(
    frame_settings,
    text='Stop',
    command=stop_repeating
)
stop_button.grid(column=1, row=4, padx=10, pady=10, sticky='NW')

# Run the application
root.mainloop()
