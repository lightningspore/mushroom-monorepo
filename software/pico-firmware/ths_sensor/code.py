# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_ahtx0


# create the I2C shared bus
i2c = busio.I2C(board.GP5, board.GP4) 
sensor = adafruit_ahtx0.AHTx0(i2c, address=56)


# while True:
#     print("Temperature: ", am.temperature)
#     print("Humidity: ", am.relative_humidity)
#     time.sleep(2)


import os

import socketpool
import wifi

from adafruit_httpserver import Server, Request, Response

ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)


@server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """
    return Response(request, f"Hello from the CircuitPython HTTP Server! {sensor.temperature}")


server.serve_forever(str(wifi.radio.ipv4_address))