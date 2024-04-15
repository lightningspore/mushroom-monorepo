try:
    import time
    import json
    import os

    import board
    import busio
    import adafruit_scd4x

    import wifi
    import socketpool
    import board
    import digitalio
    import storage
    import gc

    from adafruit_httpserver import (
        Server,
        REQUEST_HANDLED_RESPONSE_SENT,
        Request,
        FileResponse,
        Response,
    )
    from prometheus_express import (
        check_network,
        start_http_server,
        CollectorRegistry,
        Counter,
        Gauge,
        Router,
    )

    from asyncio import create_task, gather, run, sleep as async_sleep

    # local imports
    # from wifisetup import server, wifi
except Exception as e:
    import traceback

    exc_info = traceback.format_exc().splitlines()
    for line in exc_info:
        print(line)

# *** Load Environment Variables ***
location = os.getenv("LOCATION")
led_pin = os.getenv("LED_PIN")
sensor_type = "scd41"

# *** Configure Hardware Pins ***
led = digitalio.DigitalInOut(board.__dict__[led_pin])
led.direction = digitalio.Direction.OUTPUT

# PICO
# i2c = busio.I2C(board.GP5, board.GP4)

# XIAO ESP32S3
i2c = busio.I2C(board.IO5, board.IO6, frequency=100000)

# sensor = adafruit_ahtx0.AHTx0(i2c, address=56)

sensor = adafruit_scd4x.SCD4X(i2c)
print("Serial number:", [hex(i) for i in sensor.serial_number])

sensor.start_periodic_measurement()
print("Waiting for first measurement....")


# *** Configure Prometheus ***
registry = CollectorRegistry(namespace=sensor_type)

humidity_g = Gauge(
    "humidity_gauge", "humidity sensor gauge", labels=["location"], registry=registry
)
humidity_g.values = {}
humidity_val = 0

temp_g = Gauge(
    "temp_gauge", "temp sensor gauge", labels=["location"], registry=registry
)
temp_g.values = {}
temp_val = 0
tempf_val = 0


tempf_g = Gauge(
    "tempf_gauge",
    "temp sensor gauge fahrenheight",
    labels=["location"],
    registry=registry,
)
tempf_g.values = {}

co2_g = Gauge(
    "co2_gauge",
    "co2 sensor gauge ppm",
    labels=["location"],
    registry=registry,
)
co2_g.values = {}
co2_val = 0

wifi_rssi_g = Gauge(
    "wifi_rssi_gauge", "wifi_signal_rssi", labels=["location"], registry=registry
)


pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)
server.start(port=6969)
print("IP Address:", wifi.radio.ipv4_address)


# def configure_server(server):
@server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """
    return Response(request, f"Hello from the CircuitPython HTTP Server!")


@server.route("/metrics")
def metrics(request: Request):
    try:
        print("metrics")
        temp_g.labels(location).set(temp_val)
        tempf_g.labels(location).set(tempf_val)
        humidity_g.labels(location).set(humidity_val)
        co2_g.labels(location).set(co2_val)
        metrics = "\n".join(registry.render())
        # print(metrics)
        return Response(request, metrics)
    except Exception as e:
        print("Error in metrics", str(e))
        return Response(request, "Error in metrics")


@server.route("/metrics/json")
def metrics_json(request: Request):
    try:
        print("metrics json")
        metrics = {
            "tempf": tempf_val,
            "tempc": temp_val,
            "humidity": humidity_val,
            "co2": co2_val
        }
        return Response(request, json.dumps(metrics))
    except Exception as e:
        print("Error in metrics", str(e))
        return Response(request, "Error in metrics")

@server.route("/info")
def show_info(request: Request):
    try:
        print("show info")
        info_output = {
            "sensor_type": sensor_type,
            "location": location,
        }
        return Response(request, json.dumps(info_output))
    except Exception as e:
        output = f"Error in response: {str(e)}"
        print(output)
        return Response(request, output)

def connect_to_wifi():
    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    print(f"Connecting to network: {ssid}")
    print(f"Using password: {password}")
    wifi.radio.connect(ssid, password)
    print(f"Connected to: {ssid}")
    print(f"Connected to Wifi?: {wifi.radio.connected}")


def collect_sensor_data():
    global temp_val, tempf_val, humidity_val, co2_val
    try:
        if sensor.data_ready:
            temp_val = sensor.temperature
            tempf_val = temp_val * 9 / 5 + 32
            humidity_val = sensor.relative_humidity
            co2_val = sensor.CO2
            print("CO2: %d ppm" % co2_val)
            print("Temperature: %0.1f *F" % tempf_val)
            print("Humidity: %0.1f %%" % humidity_val)
            print()
    except Exception as e:
        print("Error in collect_sensor_data", str(e))
        gc.collect()


async def blinky(blink_count=1):
    led.value = 0
    time.sleep(2)

    for _ in range(blink_count):
        led.value = 1
        time.sleep(0.5)
        led.value = 0
        time.sleep(0.1)


async def sensor_loop():
    while True:
        collect_sensor_data()
        await async_sleep(5)


async def do_something_useful():
    count = 0
    while True:
        try:
            if wifi.radio.connected == False:
                await blinky(10)
                count += 1
                wifi.radio.connect(
                    os.getenv("CIRCUITPY_WIFI_SSID"),
                    os.getenv("CIRCUITPY_WIFI_PASSWORD"),
                )
                if count > 20:
                    import microcontroller

                    microcontroller.reset()
            else:
                await blinky(3)
            # Do something useful in this section,
            # for example read a sensor and capture an average,
            # or a running total of the last 10 samples
            print("IP Address:", wifi.radio.ipv4_address)

            print(f"Allocated Memory: {gc.mem_alloc()}")
            print(f"Free Memory: {gc.mem_free()}")
            print(f"Garbage Collection Enabled: {gc.isenabled()}")
            await async_sleep(1)
        except Exception as e:
            print("critical error!", str(e))
            gc.collect()
            await async_sleep(1)


async def handle_http_requests():
    while True:
        try:
            # Process any waiting requests
            pool_result = server.poll()

            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

            await async_sleep(0)
        except Exception as e:
            print("Error in handle_http_requests", str(e))
            gc.collect()
            await async_sleep(1)


async def main():

    global server
    await blinky(5)
    collect_sensor_data()

    await gather(
        create_task(handle_http_requests()),
        create_task(do_something_useful()),
        create_task(sensor_loop()),
    )


try:
    run(main())
except Exception as e:
    import microcontroller
    import traceback

    print(e)
    exc_info = traceback.format_exc().splitlines()
    print("Error!!!", str(e))
    time.sleep(10)
    # microcontroller.reset()
    while True:
        blinky(1)
        for line in exc_info:
            print(line)
        time.sleep(3)
