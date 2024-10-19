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

plug_pro = ShellyPro4PM(f"http://{device_ip}")

# Configure file logging
logging.basicConfig(filename='run_pid.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

pid_params = tuple(float(x) for x in os.environ.get('PID_PARAMS', '0.25,0.00015,0.001').split(','))
pid = PID(*pid_params, setpoint=86)
pid.set_auto_mode(False)
pid.set_auto_mode(True, last_output=81)
print(pid.components)

pid.sample_time = 300
pid.output_limits = (50, 100)

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





def set_humidity(setpoint):
    toggle_after_seconds = setpoint
    timespec_on = "0 */2 * * * *"
    turn_on = SwitchSetRequest(
        id=1,
        params=SwitchSetParams(id=humidity_switch_id, toggle_after=toggle_after_seconds, on=True),
    )
    plug_pro.schedule.update(schedule_id, True, timespec_on, calls=[turn_on])


def pid_update(average):
    next_setpoint = int(round(pid(average),0))
    logger.info(f"setting humidity controller to setpoint: {next_setpoint}")
    Pv, Iv, Dv = pid.components
    logger.info(f"PID Components: P -> {Pv}... I -> {Iv}... D -> {Dv}")
    set_humidity(next_setpoint)

async def waiting_loop():
    while True:
        try:
            current_average = run_query()
            logger.info(f"Current average humidity of last 15 mins: {current_average}. Current setpoint: {pid.setpoint}")
            if pid.time_fn() - pid._last_time > pid.sample_time:
                pid_update(current_average)
            logger.info(f"Resting for 1 minute... (-_-)zzZ")
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error setting pid loop!")
            logger.error(e)


if __name__ == "__main__":
    asyncio.run(waiting_loop())