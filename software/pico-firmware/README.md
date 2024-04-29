# pico firmware
All of the firmware is written in CircuitPython

## Install CircuitPython

### Download Firmware
```bash
# Raspberry Pi Pico W
wget https://downloads.circuitpython.org/bin/raspberry_pi_pico_w/en_US/adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.0.2.uf2

# XIAO ESP32S3
wget https://downloads.circuitpython.org/bin/espressif_esp32s3_devkitm_1_n8/en_US/adafruit-circuitpython-espressif_esp32s3_devkitm_1_n8-en_US-9.0.2.bin
```
### Flash Firmware

NEW
```
# erase and install circuitpython
./initialize.sh
```
Before it is flashed with CircuitPython it will show up (on MacOS) as:

```/dev/tty.usbmodem114301```

but after it is flashed, a serial port will appear which looks like this:
(This is the MAC address at the end BTW)

```/dev/tty.usbmodem47D4DB182240```

Now that CircuitPython is installed on our device, it will also appear on our computer as a USB port. That is where we update the code.

On MacOS it will be mounted on your system drive like so:
```
/Volumes/CIRCUITPY/
```

In order to install the application for each device, navigate to one of their device directories and run the install script.

```
cd ths_sensor
./install
```

OLD
```
# Completely erase device
esptool.py --port /dev/tty.usbmodem114301 erase_flash

# Flash CircuitPython Firmware
esptool.py \
	--port /dev/tty.usbmodem114301 --baud 460800 \
	--before default_reset --after hard_reset \
	--chip esp32s3  write_flash \
	--flash_mode dio --flash_size detect \
	--flash_freq 80m 0x0 ~/Downloads/adafruit-circuitpython-espressif_esp32s3_devkitm_1_n8-en_US-9.0.2.bin
```

## Dev tools
```
# Install circup + other dev tools
# THIS IS INSTALLING ONTO LOCAL DEV MACHINE
pip install -r requirements-dev.txt
```

## Circup
Circup is a tool for adding and updating libraries to the CircuitPython device.

```
circup install -r requirements-circuitpython.txt
```


