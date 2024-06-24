import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import Toplevel
import pandas as pd
import numpy as np
from pyswarms.single import GlobalBestPSO
import math
import matlab.engine

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

selected_file_path = ""
# Function to read the CSV file and plot the data
def display_file_content(file_path):
    try:
        data = pd.read_csv(file_path)
        plot_data(data) # calls function to plot data
        global imported_data
        imported_data = data # Store the imported data globally for optimization
    except Exception as e:
        print("Error reading file:", e)

# Function to import a file
def import_file():
    global selected_file_path
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        selected_file_path = file_path
        display_file_content(file_path)

def run_matlab_script():
    try:
        global selected_file_path
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()

        # Add the directory containing your MATLAB script to the MATLAB path
        eng.addpath(r'/Users/kimberly/Documents/MATLAB/IRES-Summer-2024', nargout=0)

        # Run the MATLAB script with the file path as an argument
        eng.ColeReplaceR1WithC(selected_file_path, nargout=0)
        
        # Keep the figures open by preventing MATLAB from closing immediately
        # input("Press Enter to close the MATLAB figures and exit...")
        
    except matlab.engine.MatlabExecutionError as e:
        print(f"MATLAB execution error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        eng.quit()

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
        ax1.semilogx(data['Frequency(Hz)'], data['Impedance(Ohm)'])
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
        ax2.semilogx(data['Frequency(Hz)'], abs(data['Phase(degrees)']))
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
        ax3.semilogx(data['Absolute Resistance(Ohm)'], abs(data['Absolute Reactance(Ohm)']))
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
root.geometry("1100x600")

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
optimization_button = tk.Button(frame_settings, text="Optimize", command=run_matlab_script) # implement command 
optimization_button.grid(column=0, row=1, padx=10, pady=10, sticky='NW')


def cole_model_impedance(frequencies, R1, R2, C_alpha, alpha):
    # s is the complex frequency variable (jω where ω = 2πf)
    omega = 2 * np.pi * frequencies
    s = 1j * omega
    Z = R1 + (R2 - R1) / (1 + (s**alpha * C_alpha * (R2 - R1)))
    return Z

def plot_cole_model():
    # Create a new window
    new_window = Toplevel()
    new_window.title("Cole Model Graph")

    # Create a frame for the plot
    frame_plots = tk.Frame(new_window)
    frame_plots.pack(fill=tk.BOTH, expand=True)

    # Generate Cole model data
    f = np.logspace(-3, 6, num=500)  # Frequency range from 10^-3 to 10^6 Hz
    R1 = 1000  # Ohm (1kΩ)
    R2 = 21000  # Ohm (21kΩ)
    C_alpha = 25e-9  # Farad (25nF)
    alpha = 0.75

    Z = cole_model_impedance(f, R1, R2, C_alpha, alpha)
    Z_real = Z.real
    Z_imag = -Z.imag  # Negative imaginary part

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(Z_real, Z_imag, 'm-', label='Cole Model')
    ax.set_xlabel('Real ($\Omega$)')
    ax.set_ylabel('-Imaginary ($\Omega$)')
    ax.set_title('Fractional-Order Single Dispersion Cole-Model')
    ax.text(0.1 * max(Z_real), 0.9 * max(Z_imag),
            '$R_1 = 1k\Omega$\n$R_2 = 21k\Omega$\n$C_\\alpha = 25nF$\n$\\alpha = 0.75$\n$F = 1mHz : 1MHz$',
            fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    ax.legend()
    ax.grid(True)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=frame_plots)
    fig.patch.set_alpha(0.0)  # Make the figure background transparent
    ax.patch.set_alpha(0.0)   # Make the axes background transparent
    canvas.get_tk_widget().configure(bg='white')  # Match the background color
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def double_cole_model_impedance(frequencies, R1, R2, R3, C_alpha, alpha, C_beta, beta):
    # s is the complex frequency variable (jω where ω = 2πf)
    omega = 2 * np.pi * frequencies
    s = 1j * omega
    Z1 = R1 + (R2 - R1) / (1 + (s**alpha * C_alpha * (R2 - R1)))
    Z2 = R3 / (1 + (s**beta * C_beta * R3))
    Z = Z1 + Z2
    return Z

def plot_double_cole_model():
    # Create a new window
    new_window = Toplevel()
    new_window.title("Double Dispersion Cole Model Graph")

    # Create a frame for the plot
    frame_plots = tk.Frame(new_window)
    frame_plots.pack(fill=tk.BOTH, expand=True)

    # Generate Double Cole model data
    f = np.logspace(-3, 6, num=500)  # Frequency range from 10^-3 to 10^6 Hz
    R1 = 42.9  # Ohm
    R2 = 71.6  # Ohm
    R3 = 16.5  # Ohm
    C_alpha = 3.086e-6  # Farad (3.086 µF)
    alpha = 0.507
    C_beta = 89.29e-6  # Farad (89.29 µF)
    beta = 0.766

    Z = double_cole_model_impedance(f, R1, R2, R3, C_alpha, alpha, C_beta, beta)
    Z_real = Z.real
    Z_imag = -Z.imag  # Negative imaginary part

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(Z_real, Z_imag, 'm-', label='Double Dispersion Cole Model')
    ax.set_xlabel('Real ($\Omega$)')
    ax.set_ylabel('-Imaginary ($\Omega$)')
    ax.set_title('Double Dispersion Cole-Model')
    ax.text(0.1 * max(Z_real), 0.9 * max(Z_imag),
            '$R_1=42.9 \Omega$\n$R_2=71.6 \Omega$\n$R_3=16.5 \Omega$\n$C_\\alpha=3.086 \mu F$\n$C_\\beta=89.29 \mu F$\n$\\alpha=0.507$\n$\\beta=0.766$\n$F=1mHz : 1MHz$',
            fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    ax.legend()
    ax.grid(True)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=frame_plots)
    fig.patch.set_alpha(0.0)  # Make the figure background transparent
    ax.patch.set_alpha(0.0)   # Make the axes background transparent
    canvas.get_tk_widget().configure(bg='white')  # Match the background color
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def wood_model_impedance(frequencies, R2, C1, alpha1, C2, alpha2):
    # s is the complex frequency variable (jω where ω = 2πf)
    omega = 2 * np.pi * frequencies
    s = 1j * omega
    Z1 = R2 / (1 + (s**alpha1 * C1 * R2))
    Z2 = R2 / (1 + (s**alpha2 * C2 * R2))
    Z = Z1 + Z2
    return Z

def plot_wood_model():
    new_window = Toplevel()
    new_window.title("Wood Tissue Model Graph")
    frame_plots = tk.Frame(new_window)
    frame_plots.pack(fill=tk.BOTH, expand=True)
    f = np.logspace(-3, 6, num=500)
    R2 = 16.5
    C1 = 769e-6
    alpha1 = 0.507
    C2 = 89.29e-6
    alpha2 = 0.766
    Z = wood_model_impedance(f, R2, C1, alpha1, C2, alpha2)
    Z_real = Z.real
    Z_imag = -Z.imag
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(Z_real, Z_imag, 'm-', label='Wood Tissue Model')
    ax.set_xlabel("Z'($\Omega$)")
    ax.set_ylabel("-Z''($\Omega$)")
    ax.set_xlim([0, 16])
    ax.set_ylim([0, 8])
    ax.text(0.5, -7.5,
            '$R_2 = 16.5 \Omega, C_1 = 769 \mu F, C_2 = 89.29 \mu F, \\alpha_1 = 0.507, \\alpha_2 = 0.766$',
            fontsize=12, ha='center', bbox=dict(facecolor='white', alpha=0.5))
    ax.grid(True)
    canvas = FigureCanvasTkAgg(fig, master=frame_plots)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    canvas.get_tk_widget().configure(bg='white')
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def single_cole_warburg_impedance(frequencies, R1, R2, C_alpha, alpha, sigma):
    omega = 2 * np.pi * frequencies
    s = 1j * omega
    Z_cole = R1 + (R2 - R1) / (1 + (s**alpha * C_alpha * (R2 - R1)))
    Z_warburg = sigma * (1 - 1j) / np.sqrt(omega)
    Z = Z_cole + Z_warburg
    return Z

def plot_single_cole_warburg_model():
    new_window = Toplevel()
    new_window.title("Single Cole Model with Warburg Element Graph")
    frame_plots = tk.Frame(new_window)
    frame_plots.pack(fill=tk.BOTH, expand=True)
    f = np.logspace(-3, 6, num=500)
    R1 = 1000
    R2 = 21000
    C_alpha = 25e-9
    alpha = 0.75
    sigma = 1.0  # Example value for Warburg coefficient
    Z = single_cole_warburg_impedance(f, R1, R2, C_alpha, alpha, sigma)
    Z_real = Z.real
    Z_imag = -Z.imag
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(Z_real, Z_imag, 'm-', label='Single Cole Model with Warburg Element')
    ax.set_xlabel("Z'($\Omega$)")
    ax.set_ylabel("-Z''($\Omega$)")
    ax.set_title('Single Cole Model with Warburg Element')
    ax.text(0.1 * max(Z_real), 0.9 * max(Z_imag),
            '$R_1 = 1k\Omega, R_2 = 21k\Omega, C_\\alpha = 25nF, \\alpha = 0.75, \\sigma = 1$',
            fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    ax.legend()
    ax.grid(True)
    canvas = FigureCanvasTkAgg(fig, master=frame_plots)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    canvas.get_tk_widget().configure(bg='white')
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def generate_model_graph():
    selected_model = model_dropdown.get()
    if selected_model == 'Single Cole Model':
        plot_cole_model()
    elif selected_model == 'Double Cole Model':
        plot_double_cole_model()
        pass
    elif selected_model == 'Wood Tissue Model':
        plot_wood_model()
        pass
    elif selected_model == 'Single Cole Model with Warburg Element':
        plot_single_cole_warburg_model()
        pass

# Button to generate model
model_button = tk.Button(frame_settings, text="Generate Model Graph", command=generate_model_graph)
model_button.grid(column=5, row=0, padx=5, pady=5, sticky='NW')

# Model label and dropdown
model_label = tk.Label(frame_settings, text="Model:")
model_label.grid(column=3, row=0, padx=5, pady=5, sticky='NW')
n = tk.StringVar
model_dropdown = ttk.Combobox(frame_settings, textvariable=n)
model_dropdown.grid(column=4,row=0, padx=5, pady=5, sticky='NW')
model_dropdown['values'] = ('Single Cole Model', 'Double Cole Model', 'Wood Tissue Model', 'Single Cole Model with Warburg Element')
 
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
