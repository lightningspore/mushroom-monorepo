# Shelly Plug Setup
This directory contains the setup code for creating Shelly plugs for a variety of situations.

## Hotplate
The hotplate is configured in two ways:
1. The hotplate control is either ON or OFF.
2. The hotplate has a schedule which when enabled, automatically turns the hotplate on at the start of each period.
3. By configuring the auto-shutoff timer, we can achieve a specified duty cycle.

Example: 
- Enable scheduled task with period of 30 seconds, which turns ON the outlet.
- Configure the outlet to auto-shutoff after 15 seconds.

## Light Control
The lights are configured to to have a schedule, where the lights turn ON at a given time, and they turn OFF at a given time.

Example: 
- Turn on Lights at 7AM
- Turn off Lights at 9PM

## Magnetic Stirrer Control
The magnetic stirrer is setup with a periodic cycle with a fixed auto-shutoff. 

Example: The magnetic stirrers might turn ON every 3 minutes, and turn OFF after running 60 seconds.
