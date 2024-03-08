import time
import json
import os


import board
import busio
import adafruit_ahtx0

import wifi
import board
import digitalio

from adafruit_httpserver import Server, Request, Response
from prometheus_express import check_network, start_http_server, CollectorRegistry, Counter, Gauge, Router

# local imports
from wifisetup import server, wifi

# create the I2C shared bus
i2c = busio.I2C(board.GP5, board.GP4) 
sensor = adafruit_ahtx0.AHTx0(i2c, address=56)

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
    'tempf_gauge',
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
    tempf_g.set(sensor.temperature * 9 / 5 + 32)
    humidity_g.set(sensor.relative_humidity)
    metrics = "\n".join(registry.render())
    #print(metrics)
    return Response(request, metrics)

@server.route("/metrics/json")
def metrics(request: Request):
    print("metrics json")
    metrics = {"tempf": sensor.temperature * 9 / 5 + 32, "tempc": sensor.temperature, "humidity": sensor.relative_humidity}
    #print(metrics)
    return Response(request, json.dumps(metrics))




def main():
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT


    i = 0
    while i < 20:
        time.sleep(0.1)
        i += 1
        led.value = i % 2

    # server.serve_forever(str(wifi.radio.ipv4_address))
    # server.serve_forever(port=80)
    server.start(port=80)
    while True:
        led.value = not led.value
        server.poll()
        time.sleep(0.5)


try:
	main()
except Exception as e:
    import microcontroller
    print("Error:\n", str(e))
    print("Resetting microcontroller in 10 seconds")
    time.sleep(10)
    microcontroller.reset()



