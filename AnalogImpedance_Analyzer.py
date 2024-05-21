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
steps = 151
start = 1e2
stop = 1e6
reference = 1e3

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
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
    rgRs[i] = abs(resistance.value) # absolute value for logarithmic plot
    rgXs[i] = abs(reactance.value)
    
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

plt.plot(rgHz, rgRs, rgHz, rgXs)
ax = plt.gca()
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()

