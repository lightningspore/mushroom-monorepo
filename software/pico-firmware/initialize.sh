#!/bin/bash


esptool.py --port /dev/tty.usbmodem114301 erase_flash

esptool.py \
	--port /dev/tty.usbmodem114301 --baud 460800 \
	--before default_reset --after hard_reset \
	--chip esp32s3  write_flash \
	--flash_mode dio --flash_size detect \
	--flash_freq 80m 0x0 ~/Downloads/adafruit-circuitpython-espressif_esp32s3_devkitm_1_n8-en_US-9.0.3.bin
