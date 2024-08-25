# SDRCAP

A software defined radio recording library in python.

Organized as a Python Pip Poetry project. Currently only limited support for RTL-SDR via pyrtlsdr package with others to be added.

## Setup

### Installing

1. Obtain pyproject.toml & poetry.lock
2. in root of project, run
```
poetry install
```
Both toml and lock files are currently version controlled

### Running

Try out the example!
```
poetry run python examples/example_usage.py
```

In general, the library is organized around you calling the 
<b>library -> hardware device interface -> functions</b>
We define the hardware device interface in the python file and class name:

For RTLSDRv4 devices:
```
from sdrcap import rtl_interface 
```

### Output

Currently the recording output supports <b>CSV</b> and <b>HDF5</b> filetypes.

### Dependencies
setuptool is needed for MACOS to import packages 

A environment setting script is set to bind the poetry environments rtlsdrlib but shouldn't be necessary if you are explicitly doing:

```
poetry run python ${target}
```
instead of:
```
poetry shell
python ${target}
```
due to differences in potential python environments.
If you want to use it run:
```
source set_env.sh
```
then run:
```
sudo -E python ${target}
```
where -E attached to sudo retains the environment variable you sourced from the shell script.

### TODO's
 For RTLSDR:
 0. Support multiple devices
 1. Support all rtlsdr.rtlsdr.BaseRtlSdr API options
 2. Support asyncio streaming
 3. Support/ expand TCP server client functions -> rtlsdr.rtlsdrtcp
 4. Add compliant encryption for data at rest, data in air
 5. Add on more advanced data transformation, interpolation, sniffing and analysis features

 In general:
 0. Solid support for receive only functionality cross SDR's
 1. GNU Radio integration/ experimentation
 2. GUI client app?

 SDR devices to add (not in order):
 0. 
 1. USRP B200mini: https://www.ettus.com/all-products/usrp-b200mini/
 2. USRP B205mini-i: 
 3. hackRF One: https://www.amazon.com/dp/B0BKH7Z2NJ/
 4. ADALM Pluto

