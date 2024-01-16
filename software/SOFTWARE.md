# Software Projects

## Temperature and Humidity Sensor
Using CircuitPython (a type of MicroPython) we can read the temperature and humidity output of an AM2301 temperature and humidity sensor device.


## Thermocouple Firmware
Using CircuitPython (a type of MicroPython) we can read the temperature output of a thermocouple.

CircuitPython download:
https://circuitpython.org/board/raspberry_pi_pico_w/

CircuitPython Library Drivers:
https://docs.circuitpython.org/projects/bundle/en/latest/drivers.html

## Shelly IoT Devices
Shelly make really cool IoT relays and power outlets. The devices run an internal webserver, and is very programmable, all without needing to use a cloud service to control the device.

## Pressure Cooker OpenCV
Using OpenCV we can scan the pressure gauge of a Presto pressure cooker, and determine the current internal pressure.

## PID Loop
Using the ShellyUS IoT plug, and either the pressure cooker OpenCV, or data from a thermocouple, we can control the temperature of a hotplate. This allows us to automate the pasteurization of substrate and/or the sterilization of grains.