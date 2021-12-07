# SpaceBase
The Raspberry Pi based greenhose control system.

## Key features 

Spacebase aims to fully automate a greenhouse, including:

* automated opening and closing of windows, based on temperature, as well as time of day
* automated irrigation of plants
* water-reservoir management
* emergency defrosting

## Basic use

1. Clone this repository into the pi-users home directory and copy the autostart file into the autostart directoy. 
2. connect hardware modules
3. reboot
4. ???
5. profit

To manually start Spacebase simply execute `sudo python3 spacebase.py` inside the src folder. Mind that sudo is required for keyboard access.

## Autostart

Place the greenhouse.desktop file in  `/home/pi/.config/autostart` and modify the path to spacebase.py.

## Configuration

In the config file temperatures are stated in °Celsius. Time is stated in Seconds.

## Hardware modules

Most hardware modules are based on Arduinos. When plugged into the control system via USB they should automatically be detected on startup.

## Manual controls

keyboard keys are bound as followes:

`1` - force close windows
`2` - force open windows
`3` - set windows to atomated mode
`4` - run window recalibration cycle
`7` - toggle heater on/off

## Far future planned features

* control of energy curtains
* light-control
* air-circulation
* geothermal air-conditioning