import time
import serial
from ishelly.client import ShellyPlug


# PID coefficients
Kp = 5
Ki = 0.01
Kd = 10


# Replace '/dev/tty.board_name' with the appropriate serial port name
serial_port = '/dev/tty.usbmodem11101'
baud_rate = 115200  # Adjust as needed

loop_time_interval = 30


plug_1 = ShellyPlug("http://192.168.1.201")


def read_temperature_manual():
    temp = int(input("whats the temp yo: "))
    return temp

def set_heater_power(level):
    # level = 0-100
    print(f"using power level: {level}")
    # return 0
    old_config = plug_1.switch.get_config()
    new_config = old_config.model_copy()
    new_config.initial_state = "on"
    new_auto_off_interval = max(1, int(level * 0.01 * loop_time_interval))
    print(f"new on/off interval seconds: {new_auto_off_interval}")
    # note: use the auto_off_delay as the control factor for a pid loop!!!
    new_config.auto_off_delay = new_auto_off_interval
    plug_1.switch.set_config(new_config)


def pid_loop():
    # Initialize PID terms
    integral = 0
    previous_error = 0
    previous_time = time.time()
    setpoint = 175  # Desired temperature
    while True:
        # Measure the current temperature
        current_temperature = read_temp_from_serial()
        print(f"CURRENT temp: {current_temperature}")
        print(f"SETPOINT temp: {setpoint}")
        # Calculate error
        error = setpoint - current_temperature
        # Get the current time
        current_time = time.time()
        # Calculate time_delta
        time_delta = current_time - previous_time
        # P term
        P_out = Kp * error
        # I term
        integral += error * time_delta
        I_out = Ki * integral
        # D term
        derivative = (error - previous_error) / time_delta
        D_out = Kd * derivative
        # PID Output
        PID_output = P_out + I_out + D_out
        print(f"Pout {P_out} + Iout {I_out} + Dout {D_out} = {PID_output}")
        # Apply the heating power (PID output) to the heater
        pid_output_normalized = max(min(PID_output, 100), 1)
        set_heater_power(pid_output_normalized)
        # Save current error and time for next iteration
        previous_error = error
        previous_time = current_time
        print(f"sleeping {loop_time_interval} seconds before running PID again")
        # Wait some time before next measurement
        time.sleep(loop_time_interval)




def read_temp_from_serial():
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        # Read a line from the serial port
            data = ser.readline().decode('utf-8').rstrip()
            print(data)
            result = float(data)
            return result
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None


from ishelly.components.schedule import *
from ishelly.components.shelly import *
from ishelly.components.switch import *

device_rpc_url = "http://192.168.1.201/rpc"


job = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=0, on=True),
)

# every minute
timespec1 = "0 * * * * *"

# every 30 seconds
timespec1 = "*/30 * * * * *"

# CREATE NEW scheduled tasks
req = ScheduleCreateRequest(
    id=1,
    params=ScheduleCreateParams(
        enable=True, timespec=timespec1, calls=[job.model_dump()]
    ),
)

response = post(device_rpc_url, json=req.model_dump())
schedule_create_1 = ScheduleCreateResponse(**response.json()["result"])




req = ScheduleListRequest(id=1)
response = post(device_rpc_url, json=req.model_dump())
scheduled_tasks = ScheduleListResponse(**response.json()["result"])

print(f"There are {len(scheduled_tasks.jobs)} scheduled tasks currently saved.")



req = ScheduleDeleteRequest(
    id=1,
    params=ScheduleDeleteParams(id=3),
)
response = post(device_rpc_url, json=req.model_dump())
schedule_delete = ScheduleDeleteResponse(**response.json()["result"])


for job in scheduled_tasks.jobs:
    req = ScheduleDeleteRequest(
        id=1,
        params=ScheduleDeleteParams(id=job.id),
    )
    response = post(device_rpc_url, json=req.model_dump())
    schedule_delete = ScheduleDeleteResponse(**response.json()["result"])
    print(schedule_delete)