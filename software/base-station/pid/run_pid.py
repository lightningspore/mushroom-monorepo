import os
import pickle
from time import sleep
import logging

from ishelly.client import ShellyPro4PM
from ishelly.client import SwitchSetRequest, SwitchSetParams

from simple_pid import PID
from dotenv import load_dotenv

from prometheus_query import run_query

# Configure file logging
logging.basicConfig(filename='run_pid.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

plug_pro = ShellyPro4PM(f"http://192.168.1.125")

pid = PID(0.1, 0.0001, 0.001, setpoint=86)
pid.set_auto_mode(False)
pid.set_auto_mode(True, last_output=81)
print(pid.components)

pid.sample_time = 300
pid.output_limits = (50, 100)

def set_humidity(setpoint):
    humidity_switch_id = 0
    toggle_after_seconds = setpoint
    timespec_on = "0 */2 * * * *"
    turn_on = SwitchSetRequest(
        id=1,
        params=SwitchSetParams(id=humidity_switch_id, toggle_after=toggle_after_seconds, on=True),
    )
    plug_pro.schedule.update(5, True, timespec_on, calls=[turn_on])


def pid_update(average):
    next_setpoint = int(round(pid(average),0))
    logger.info(f"setting humidity controller to setpoint: {next_setpoint}")
    Pv, Iv, Dv = pid.components
    logger.info(f"PID Components: P -> {Pv}... I -> {Iv}... D -> {Dv}")
    set_humidity(next_setpoint)

def waiting_loop():
    while True:
        try:
            current_average = run_query()
            logger.info(f"Current average humidity of last 15 mins: {current_average}")
            if pid.time_fn() - pid._last_time > pid.sample_time:
                pid_update(current_average)
            logger.info(f"Resting for 1 minute... (-_-)zzZ")
            sleep(60)
        except Exception as e:
            logger.error(f"Error setting pid loop!")
            logger.error(e)


if __name__ == "__main__":
    waiting_loop()