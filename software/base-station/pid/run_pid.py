import os
import pickle
from time import sleep
import logging
import asyncio

from ishelly.client import ShellyPro4PM
from ishelly.client import SwitchSetRequest, SwitchSetParams

from simple_pid import PID
from dotenv import load_dotenv

from pid.prometheus_query import run_query

load_dotenv()

humidity_switch_id = int(os.getenv("HUMIDITY_SWITCH_ID", "0"))
schedule_id = int(os.getenv("SCHEDULE_ID", "5"))
device_ip = os.getenv("DEVICE_IP", "192.168.1.125")

plug_pro = None
# ShellyPro4PM(f"http://{device_ip}")

# Configure file logging
logging.basicConfig(filename='run_pid.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

pid_params = tuple(float(x) for x in os.environ.get('PID_PARAMS', '0.25,0.00015,0.001').split(','))

# Set a default PID setpoint
# Since it will default to this on bootup
# TODO: Save the setpoint to disk, and use the disk setpoint if available
default_setpoint = float(os.environ.get('HUMIDITY_SETPOINT', '85'))
pid = PID(*pid_params, setpoint=default_setpoint)
pid.set_auto_mode(False)
pid.set_auto_mode(True, last_output=81)
print(pid.components)

pid.sample_time = 300
# For our base use-case, we are adjusting the duty cycle out of 120 seconds
# This allows us to set the max and min output time out of 120 seconds
output_limits_tuple = tuple(float(x) for x in os.environ.get('OUTPUT_LIMITS', '50,110').split(','))
pid.output_limits = output_limits_tuple

# PID formula
# output = 
#    Kp * error + 
#    Ki * error * time_increment + 
#    Kd * (error - previous_error) / time_increment

# Example: Sensor is 4% away from setpoint
# output = 
#    0.25 * 4 +          # 1
#    0.0002 * 4 * 300 +  # 0.12
#    5 * (4-3) / 300 # miniscule



def initialize_shelly():
    global plug_pro
    plug_pro = ShellyPro4PM(f"http://{device_ip}")


def set_humidity(setpoint):
    try:
        toggle_after_seconds = setpoint
        timespec_on = "0 */1 * * * *"
        turn_on = SwitchSetRequest(
            id=1,
            params=SwitchSetParams(id=humidity_switch_id, toggle_after=toggle_after_seconds, on=True),
        )
        plug_pro.schedule.update(schedule_id, True, timespec_on, calls=[turn_on])
    except Exception as e:
        logger.error(f"function set_humidity error: {e}")
        raise e


def pid_update(average):
    try:
        next_setpoint = int(round(pid(average),0))
        logger.info(f"Humidifier will stay on for: ({next_setpoint} seconds)")
        Pv, Iv, Dv = pid.components
        logger.info(f"PID Components: P -> {Pv}... I -> {Iv}... D -> {Dv}")
        set_humidity(next_setpoint)
    except Exception as e:
        logger.error(f"function pid_update error: {e}")
        raise e

async def waiting_loop():
    while True:
        try:
            current_average = run_query()
            logger.info(f"Current average humidity of last 15 mins: {current_average}")
            logger.info(f"Current setpoint: {pid.setpoint}")
            if pid.time_fn() - pid._last_time > pid.sample_time:
                pid_update(current_average)
            logger.info(f"Resting for 1 minute... (-_-)zzZ")
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error setting pid loop!")
            logger.error(e)


if __name__ == "__main__":
    asyncio.run(waiting_loop())