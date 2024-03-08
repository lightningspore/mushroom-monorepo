try:
    import time
    import json
    import os

    import board
    import busio
    import adafruit_ahtx0

    import wifi
    import socketpool
    import board
    import digitalio
    import storage


    from adafruit_httpserver import Server, Request, Response
    from prometheus_express import check_network, start_http_server, CollectorRegistry, Counter, Gauge, Router

    from adafruit_httpserver import Server
    # local imports
    # from wifisetup import server, wifi
except Exception as e:
    import traceback
    exc_info = traceback.format_exc().splitlines()
    for line in exc_info:
        print(line)


# *** Configure Hardware Pins ***
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

i2c = busio.I2C(board.GP5, board.GP4) 
sensor = adafruit_ahtx0.AHTx0(i2c, address=56)


# *** Configure Prometheus ***
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

def connect_to_wifi():
    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    print(f"Connecting to network: {ssid}")
    print(f"Using password: {password}")
    wifi.radio.connect(ssid, password)
    print(f"Connected to: {ssid}")
    print(f"Connected to Wifi?: {wifi.radio.connected}")

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

# def configure_server(server):
@server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """
    return Response(request, f"Hello from the CircuitPython HTTP Server!")

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


def blinky(blink_count=1):
    led.value = 0
    time.sleep(2)

    for _ in range(blink_count):
        led.value = 1
        time.sleep(0.5)
        led.value = 0
        time.sleep(0.1)




def main():

    global server
    blinky(5)

    # i = 0
    # while i < 20:
    #     time.sleep(0.1)
    #     i += 1
    #     led.value = i % 2

    # connect_to_wifi()
    while wifi.radio.connected == False:
        blinky(5)
    
    

    # Configure the server with routes
    # configure_server(server)

    # server.serve_forever(str(wifi.radio.ipv4_address))
    # server.serve_forever(port=80)
    server.start(port=6969)
    while True:
        blinky(3)
        server.poll()
        time.sleep(2)


try:
    main()
except Exception as e:
    import microcontroller
    import traceback
    exc_info = traceback.format_exc().splitlines()
    print("Error!!!", str(e))
    time.sleep(10)
    # microcontroller.reset()
    while True:
        blinky(1)
        for line in exc_info:
            print(line)
        time.sleep(3)




