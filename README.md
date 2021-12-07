# SpaceBase

The Raspberry Pi based greenhouse control system. 

Spacebase aims to fully automate a greenhouse in a way that is easy to use and expand. The ultimate goal is to be able to put your plants in a greenhouse, fire up Spacebase and leave your plants alone until it is time to harvest. I started developing this project to bridge the gap between my love for gardening and tinkering with electronics... and because i keep forgetting to water my vegetables. 

As the name kind of suggests, i got inspired by the spacebucket community. You can probably use SpaceBase to control a spacebucket as well. 

## Key features 

* automated opening and closing of windows, based on temperature, as well as time of day
* automated irrigation of plants
* water-reservoir management
* emergency defrosting
* logging and displaying information like soil-moisture, temperature and humidity and sun-exposure

## Basic use

1. Clone this repository into the pi-users home directory and copy the autostart file into the autostart directoy. 
2. connect hardware modules
3. reboot
4. ???
5. profit

To manually start Spacebase simply execute `sudo python3 spacebase.py` inside the system folder. Mind that sudo is required for keyboard access.

## Autostart

Place the greenhouse.desktop file in  `/home/pi/.config/autostart` and modify the path to spacebase.py.

## Configuration

In the config file temperatures are stated in °Celsius. Time is stated in Seconds.

## Hardware modules / Serial API

Most hardware modules are based on Arduinos. When plugged into the control system via USB they should automatically be detected on startup. I will make a detailed documentation for the Serial API available as soon as i get to it, so you can integrate your own hardware.

## Manual controls

keyboard keys are bound as followes:

`1` force close windows

`2` force open windows

`3` set windows to atomated mode

`4` run window recalibration cycle

`7` toggle heater on/off

## Planned features

* web-based dashboard
* webcam integration
* REST-API

## Far future planned features

* control of energy curtains
* light-control
* air-circulation and -ventilation
* geothermal AC
* general/modular AC
* integration into Home Assistant
* support for multiple greenhouses