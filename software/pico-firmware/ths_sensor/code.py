# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_am2320
import busio

# create the I2C shared bus
i2c = busio.I2C(board.GP5, board.GP4) 
am = adafruit_am2320.AM2320(i2c, address=56)

while True:
    print("Temperature: ", am.temperature)
    print("Humidity: ", am.relative_humidity)
    time.sleep(2)