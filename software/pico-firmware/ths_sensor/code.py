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


from prometheus_express import check_network, start_http_server, CollectorRegistry, Counter, Gauge, Router

registry = CollectorRegistry(namespace="pico_dht20")

humidity_g = Gauge(
    'humidity_gauge',
    'humidity sensor gauge',
    labels=['ip'],
    registry=registry
)

temp_g = Gauge(
    'temp_gauge',
    'temp sensor gauge',
    labels=['ip'],
    registry=registry
)

tempf_g = Gauge(
    'temp_gauge',
    'temp sensor gauge fahrenheight',
    labels=['ip'],
    registry=registry
)

wifi_rssi_g = Gauge(
    'wifi_rssi_gauge',
    'wifi_signal_rssi',
    labels=['ip'],
    registry=registry
)


@server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """
    temp_g.set(sensor.temperature)
    humidity_g.set(sensor.relative_humidity)
    return Response(request, f"Hello from the CircuitPython HTTP Server! {sensor.temperature}")

@server.route("/metrics")
def metrics(request: Request):
    print("metrics")
    temp_g.set(sensor.temperature)
    humidity_g.set(sensor.relative_humidity)
    metrics = "\n".join(registry.render())
    #print(metrics)
    return Response(request, metrics)



server.serve_forever(str(wifi.radio.ipv4_address))