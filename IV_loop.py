import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime

# Connect to the instrument
rm = pyvisa.ResourceManager()
inst = rm.open_resource('GPIB0::16::INSTR')  # Replace with your instrument address
inst.timeout = 5000  # Set timeout in milliseconds

# Turn on interactive mode
plt.ion()

# Initialize the figure and subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))

# Initialize data lists for the three plots
Times, voltagesor = [], []
Times, currents = [], []
voltagesor, currents = [], []

# Create the line objects with different markers for each plot
line1, = ax1.plot(Times, voltagesor, 'bo-', label='Plot 1')  # Blue line with circle marker
line2, = ax2.plot(Times, currents, 'gs--', label='Plot 2')  # Green dashed line with square marker
line3, = ax3.plot(voltagesor, currents, 'r^:', label='Plot 3')  # Red dotted line with triangle marker

# Set labels and titles
#ax1.set_title('V-t plot')
ax1.set_xlabel('Time (sec)')
ax1.set_ylabel('Voltage (V)')

#ax2.set_title('I-t plot')
ax2.set_xlabel('Time (sec)')
ax2.set_ylabel('Current (A)')

#ax3.set_title('I-V Loop plot')
ax3.set_xlabel('Voltage (V)')
ax3.set_ylabel('Current (A)')


# Creat unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
filename_csv = 'IV_loop' + time_for_name +'.csv'
filename_pdf = 'IV_loop' + time_for_name +'.pdf'

# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
        writer.writerow(["Timestamp / Sec" , "Voltage / V", "Current / A"])

def generate_array(max_value, step):
    """Generates an array with the specified pattern."""

    # Part 1: 0 to positive maximum value
    pos_part = np.arange(0, max_value + step, step)

    # Part 2: Positive maximum value to negative maximum value
    neg_part = np.arange(max_value, -max_value - step, -step)

    # Part 3: Negative maximum value to 0
    zero_part = np.arange(-max_value, step, step)

    # Combine the three parts
    return np.concatenate([pos_part, neg_part, zero_part])

# usage
max_value = 5.0
step = 0.2
voltages = generate_array(max_value, step)

# Initialize current array
currents = []

# Configure the 6517B
inst.write("*RST")  # Reset the instrument
inst.write("SYST:ZCH ON") # Zero check ON
inst.write(":FUNC 'CURR'") # measuring current
inst.write("SYST:ZCH OFF") # Zero check OFF
inst.write(":CURR:RANG:AUTO ON")  # Set current range to Auto (adjust as needed)
inst.write(":FORM:ELEM READ")  # Set output format
start_time = time.time() # intial time
# Perform the IV sweep
for voltage in voltages:
    inst.write(f":SOUR:VOLT {voltage}")  # Set the voltage
    inst.write(":OUTP ON")  # Turn output on
    time.sleep(1)
    current = float(inst.query(":READ?"))  # Extract the current value
    elapsed_time = time.time() - start_time  # instrument time to measure the current
    voltagesor.append(voltage) # save voltage data in an array
    currents.append(current)  # save current data in an array
    Times.append(elapsed_time) # save measured time in an array
    print(f"Time: {elapsed_time} sec, Voltage: {voltage:.3f} V, Current: {current:.6e} A")  #print the values while code is running
    
    line1.set_xdata(Times)  # Update x-data of the line
    line1.set_ydata(voltagesor)  # Update y-data of the line
    ax1.relim()  # Recalculate limits for updated data
    ax1.autoscale_view(True, True, True)  # Autoscale the axes
   
    line2.set_xdata(Times)  # Update x-data of the line
    line2.set_ydata(currents)  # Update y-data of the line
    ax2.relim()  # Recalculate limits for updated data
    ax2.autoscale_view(True, True, True)  # Autoscale the axes

    line3.set_xdata(voltagesor)  # Update x-data of the line
    line3.set_ydata(currents)  # Update y-data of the line
    ax3.relim()  # Recalculate limits for updated data
    ax3.autoscale_view(True, True, True)  # Autoscale the axes

    plt.draw()  # Update the figure
    plt.pause(0.01)  # Pause for half a second between measurements
    inst.write(":OUTP OFF")  # Turn output off
# Write the data in a csv
    with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
        writer.writerow([elapsed_time, voltage, current])

# Close the instrument connection
inst.close()

plt.savefig('IV loop')
plt.ioff()  # Turn off interactive mode
plt.show()  # Show the final plot

# Plot the IV curve
#plt.plot(voltages, currents, marker='o')
#plt.xlabel('Voltage (V)')
#plt.ylabel('Current (A)')
#plt.title('IV Curve')
#plt.show()