#!/bin/bash

if [ -e /dev/tty.usbmodem114301 ]; then
    echo "/dev/tty.usbmodem114301 exists, proceeding with flash operation."
else
    echo "/dev/tty.usbmodem114301 does not exist, please check your connection."
    # exit 1
	if ls /dev/tty.usbmodem* 1> /dev/null 2>&1; then
    echo "Detected devices:"
    ls /dev/tty.usbmodem* | while read modem; do
        if [[ $modem =~ tty.usbmodem([0-9A-F]{12})$ ]]; then
            echo "Device with MAC address ${BASH_REMATCH[1]} is connected."
        else
            echo "$modem does not match the expected pattern."
        fi
    done
    echo "A device with CircuitPython installed is detected. No need to reflash."
    # exit 2
	fi
fi

ls /dev/tty.usbmodem* | while read modem; do
		echo "$modem"
	if [[ $modem =~ tty.usbmodem([0-9A-Fa-f]{12})$ ]]; then
		
		echo "Device with MAC address ${BASH_REMATCH[1]} is connected."
	else
		echo "$modem does not match the expected pattern."
	fi
done
exit 1

esptool.py --port /dev/tty.usbmodem114301 erase_flash

esptool.py \
	--port /dev/tty.usbmodem114301 --baud 460800 \
	--before default_reset --after hard_reset \
	--chip esp32s3  write_flash \
	--flash_mode dio --flash_size detect \
	--flash_freq 80m 0x0 ~/Downloads/adafruit-circuitpython-espressif_esp32s3_devkitm_1_n8-en_US-9.0.3.bin
