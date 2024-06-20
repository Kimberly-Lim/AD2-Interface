import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import math
import numpy as np
from pyswarms.single import GlobalBestPSO

# Frequency values dictionary
frequency_values = {
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

freq_keys = list(frequency_values.keys())

# Function to read the CSV file and plot the data
# # def display_file_content(file_path):
#     try:
#         data = pd.read_csv(file_path)
#         plot_data(data) # calls function to plot data
#         global imported_data
#         imported_data = data # Store the imported data globally for optimization
#     except Exception as e:
#         print("Error reading file:", e)

def display_file_content(file_path):
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            plot_data(data)
            global imported_data
            imported_data = data  # Store the imported data globally for optimization
            return  # Exit the function if the file is read successfully
        except Exception as e:
            print(f"Error reading file with encoding {encoding}: {e}")
    print("Failed to read the file with all tested encodings.")

# Function to import a file
def import_file():
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        display_file_content(file_path)

# Single Cole Model
# def cole_model(params, freq): 
#     global s, w
#     s = 1*j * w 
#     w = 2*math.pi*freq
    # params = [alpha1, C1, R1, R2, alpha2, C2, alpha3, C3]

# Function to optimize
# def optimize():
#     global freq, angle, Rs, Xs, Mag, Data, s, best_params, Rs_est, Xs_est
    
#     data = imported_data
    
    
#     freq = data['Frequency(Hz)'] # Retrieving data from the .csv files
#     angle = data['Phase(degrees)']
#     Rs = data['Absolute Resistance(Ohm)']
#     Xs = data['Absolute Reactance(Ohm)']
#     Mag = (math.sqrt((Rs^2) + (Xs^2))) # Magnitude of resistance and reactance squared 
#     Data = Mag * (math.exp(1j * angle * (math.pi/180))) # 1j is a imaginary number in python

#     w = 2 * math.pi * freq
#     s = 1j * w

#     # Impedance function
#     def fun(P, s):
#         term1 = 1 / ((s**P[0]) * P[1])
#         term2 = P[2] / (1 + (s**P[4]) * P[2] * P[5])
#         term3 = P[3] / (1 + (s**P[6]) * P[3] * P[7])
#         return term1 + term2 + term3

#     # def obj_fun(params, s, experimental_data):
#         model_data = fun(params, s)
#         real_error = np.real(experimental_data) - np.real(experimental_data)
#         imag_error = np.imag(experimental_data) - np.imag(experimental_data)
#         error = real_error**2 + imag_error**2

#         return np.sum(error)


#     # Objective function
#     def obj_fun(P):
#         modeled_data = fun(P, s)
#         real_error = np.real(Data) - np.real(modeled_data)
#         imag_error = np.imag(Data) - np.imag(modeled_data)
#         error = real_error**2 + imag_error**2
#         return np.sum(error)

#     # Bounds for the optimization
#     lb = [0, 0, 0, 0, 0, 0, 0, 0]
#     ub = [1, 100e-6, 1e6, 250e3, 1, 100e-6, 1, 100e-6]
#     bounds = (lb, ub)

#     # PSO parameters
#     options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}

#     # Perform PSO optimization
#     optimizer = GlobalBestPSO(n_particles=100, dimensions=8, options=options, bounds=bounds)
#     cost, best_params = optimizer.optimize(obj_fun, iters=2000)

#     # Estimate the impedance using the best parameters
#     best_modeled_data = fun(best_params, s)
#     Rs_est = np.abs(best_modeled_data) * np.cos(np.angle(best_modeled_data))
#     Xs_est = np.abs(best_modeled_data) * np.sin(np.angle(best_modeled_data))

#     plot_optimization_data()


# # Function to plot the optimized data
# def plot_optimization_data():
#     plt.figure(figsize=(12, 8))

#     plt.subplot(2, 1, 1)
#     plt.semilogx(freq, Rs_est, 'r--', label='Approximation')
#     plt.semilogx(freq, Rs, 'g--', label='Known')
#     plt.grid(True, which='both')
#     plt.xlabel('Frequency [Hz]')
#     plt.ylabel('Magnitude [Ohms]')
#     plt.legend()
#     plt.title('Approx vs Known - Magnitude')

#     plt.subplot(2, 1, 2)
#     plt.semilogx(freq, Xs_est, 'r--', label='Approximation')
#     plt.semilogx(freq, Xs, 'g--', label='Known')
#     plt.grid(True, which='both')
#     plt.xlabel('Frequency [Hz]')
#     plt.ylabel('Phase [Ohms]')
#     plt.legend()
#     plt.title('Approx vs Known - Phase')

#     plt.tight_layout()
#     plt.show()

#     # Nyquist plot
#     plt.figure()
#     plt.plot(Rs_est, -Xs_est, '.', linewidth=2, color=[0.6350, 0.0780, 0.1840], label='Estimated')
#     plt.plot(Rs, -Xs, '.', linewidth=2, color=[0.3010, 0.7450, 0.9330], label='Actual')
#     plt.xlabel("Rs")
#     plt.ylabel("-Xs")
#     plt.title("Nyquist plot")
#     plt.legend()
#     plt.show()

#     # Percent difference calculations
#     Rs_diff = np.abs(100 * (Rs_est - Rs) / Rs)
#     Xs_diff = np.abs(100 * (Xs_est - Xs) / Xs)

#     # Percent difference plotted over all frequencies
#     plt.figure(figsize=(12, 8))

#     plt.subplot(2, 1, 1)
#     plt.semilogx(freq, Rs_diff)
#     plt.xlabel("Frequency [Hz]")
#     plt.ylabel("Rs percent difference")
#     plt.title("Rs Difference")

#     plt.subplot(2, 1, 2)
#     plt.semilogx(freq, Xs_diff)
#     plt.xlabel("Frequency [Hz]")
#     plt.ylabel("Xs percent difference")
#     plt.title("Xs Difference")

#     plt.tight_layout()
#     plt.show()

# Function to plot data
def plot_data(data):
    # Clear existing plots
    for widget in frame_plots.winfo_children():
        widget.destroy()
    # Check if necessary columns exist
    required_columns = {'Frequency(Hz)', 'Impedance(Ohm)', 'Phase(degrees)', 'Absolute Resistance(Ohm)', 'Absolute Reactance(Ohm)'}
    if required_columns.issubset(data.columns):
        # Create frequency vs. magnitude plot
        fig1, ax1 = plt.subplots(figsize=(2,1))
        ax1.plot(data['Frequency(Hz)'], data['Impedance(Ohm)'])
        ax1.set_xlabel('Frequency')
        ax1.set_ylabel('Magnitude')
        ax1.set_title('Frequency vs Magnitude')
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_plots)
        fig1.patch.set_alpha(0.0)  # Make the figure background transparent
        ax1.patch.set_alpha(0.0)   # Make the axes background transparent
        canvas1.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Create frequency vs. phase plot
        fig2, ax2 = plt.subplots(figsize=(2,1))
        ax2.plot(data['Frequency(Hz)'], abs(data['Phase(degrees)']))
        ax2.set_xlabel('Frequency')
        ax2.set_ylabel('Phase')
        ax2.set_title('Frequency vs Phase')
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_plots)
        fig2.patch.set_alpha(0.0)  # Make the figure background transparent
        ax2.patch.set_alpha(0.0)   # Make the axes background transparent
        canvas2.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        # Create resistance vs. -reactance plot
        fig3, ax3 = plt.subplots(figsize=(2,1))
        ax3.plot(data['Absolute Resistance(Ohm)'], abs(data['Absolute Reactance(Ohm)']))
        ax3.set_xlabel('Resistance')
        ax3.set_ylabel('-Reactance')
        ax3.set_title('Resistance vs -Reactance')
        canvas3 = FigureCanvasTkAgg(fig3, master=frame_plots)
        fig3.patch.set_alpha(0.0)  # Make the figure background transparent
        ax3.patch.set_alpha(0.0)   # Make the axes background transparent
        canvas3.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
        canvas3.draw()
        canvas3.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky='nsew')
    else:
        print("Error: The required columns are not present in the data.")

# Create main window
root = tk.Tk()
root.title("Optimization")
default_bg_color = root.cget('bg')

# Set the window size
root.geometry("1200x600")

# Create a frame for the settings
frame_settings = tk.Frame(root, bg=default_bg_color)
frame_settings.grid(row=0, column=0, rowspan=1, columnspan=1, padx=10, pady=10, sticky='nsew')

# Create a frame for the plots
frame_plots = tk.Frame(root, bg=default_bg_color)
frame_plots.grid(row=2, column=0, rowspan=2, columnspan=3, padx=10, pady=10, sticky='nsew')

# Button for import file
import_button = tk.Button(frame_settings, text="Import File", command=import_file)
import_button.grid(column=0, row=0, padx=10, pady=10, sticky='NW')

# Button for optimization
optimization_button = tk.Button(frame_settings, text="Optimize") # implement command 
optimization_button.grid(column=0, row=1, padx=10, pady=10, sticky='NW')

# Model label and dropdown
model_label = tk.Label(frame_settings, text="Model:")
model_label.grid(column=3, row=0, padx=5, pady=5, sticky='NW')
n = tk.StringVar
model_dropdown = ttk.Combobox(frame_settings, textvariable=n)
model_dropdown.grid(column=4,row=0, padx=5, pady=5, sticky='NW')
model_dropdown['values'] = ('Cole Model', 'Double Cole Model', 'Wood Tissue Model', 'Single Cole Model with Warburg Element')
 
# Lower Bound Frequency
slider_label1 = tk.Label(frame_settings, text="Lower Bound Frequency:")
slider_label1.grid(column=1, row=0, padx=5, pady=5, sticky='NW')
slider1 = ttk.Entry(frame_settings)
slider1.grid(column=2, row=0, padx=5, pady=5, sticky='NW')

# Upper Bound Frequency
slider_label2 = tk.Label(frame_settings, text="Upper Bound Frequency:")
slider_label2.grid(column=1, row=1, padx=5, pady=5, sticky='NW')
slider2 = ttk.Entry(frame_settings)
slider2.grid(column=2, row=1, padx=5, pady=5, sticky='NW')

# Make the main window's grid layout adjustable
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=3)
root.rowconfigure(3, weight=3)

# Make the frame expand with the window
frame_plots.columnconfigure(0, weight=1)
frame_plots.columnconfigure(1, weight=1)
frame_plots.columnconfigure(2, weight=1)
frame_plots.rowconfigure(0, weight=1)
frame_plots.rowconfigure(1, weight=1)
frame_plots.rowconfigure(2, weight=1)

# Configure grid layout for frame_settings
frame_settings.columnconfigure(0, weight=1)
frame_settings.columnconfigure(1, weight=1)
frame_settings.columnconfigure(2, weight=1)
frame_settings.rowconfigure(0, weight=1)
frame_settings.rowconfigure(1, weight=1)

# Run the application
root.mainloop()
