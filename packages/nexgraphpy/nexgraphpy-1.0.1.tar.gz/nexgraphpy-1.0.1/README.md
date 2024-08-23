# nexgraphpy module
# Nexgraph Python

## Description:
NexGraph Python is a Python library implementation of the NexGraph software which works with Nextech brand force gauges.  It provides an easy way to connect to Nextech force gauges using Python.  Despite it's name it does not create graphs as of yet, but does retrieve data from the data to be graphed.

This library is under development and more features will be added later.

## Requirements:
Tested on Python versions 3.10+

## Installation:

`pip install nexgraphpy`

## Examples:

### Import the library:

`from nexgraph import NexGraph`

### Create a new instance:

`dft_force_gauge = NexGraph()`

### Find and connect to a Nextech force gauge over USB serial port:

```
if dft_force_gauge.find():
    if dft_force_gauge.connect():
        print(dft_force_gauge.get_info())
        dft_force_gauge.disconnect()
        dft_force_gauge = None
    else:
        print("Unable to connect")
        exit()
else:
    print("No device found.")
    exit()
```

### Connect to a Nextech force gauge directly:

```
# Initialize with device the path
dft_force_gauge = NexGraph("COM3")

# Or set the device path after initializing
dft_force_gauge.device_path = "COM3"

# Connect to device after setting the path
if dft_force_gauge.connect():
    ...
```

### Basic device serial operations:

#### Returns boolean value
```
# Change device modes, peak and tracking
dft_force_gauge.mode()

# Change the units on device
dft_force_gauge.unit()

# Reset the current device value
dft_force_gauge.reset()

# Zero (Tare) the value on device
dft_force_gauge.zero()
```

#### Returns string value
```
# Download data from device memory
dft_force_gauge.download()

# Print current value
dft_force_gauge.print_value()

# Print peak compression value
dft_force_gauge.peak_compression()

# Print peak tension value
dft_force_gauge.peak_tension()

# Print different formatted outputs
dft_force_gauge.long_output()
dft_force_gauge.short_output()
dft_force_gauge.mini_output()
```

### Output live data of 100 rows:

*Note: 
The output rate is roughly 10 data points per second.
100 data points is approximately 10 seconds of testing.*

```
i = 0
while True:
    print(dft_force_gauge.long_output())
    i += 1
    if i >= 100:
        break
```
## Documentation

[Nexgraph Python Docs](https://python.nexgraphapp.com/)
<https://python.nexgraphapp.com/>