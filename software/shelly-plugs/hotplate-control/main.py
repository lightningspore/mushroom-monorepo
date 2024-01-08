from pprint import pprint
from requests import post


from ishelly.components.switch import *
from ishelly.components.schedule import *
from ishelly.components.shelly import *
from ishelly.client import ShellyPlug

### DETAILS:
### This
### This code is intended to control an electric hotplate, which is powered using a 
### Shelly PlugUS which is setup and running on your network.
### Mine is running at `http://192.168.1.201`.
### We create 1 scheduled events for the device: Every 30 seconds we will turn the output to the ON state.
### Based on sensor reading or some other input, we will set the DUTY CYCLE.
### This means for 50% duty cycle: T=0 -> Power = ON, T=15 -> Power = OFF, T=30 -> Power = ON, T=45 -> Power = OFF


device_rpc_url = "http://192.168.1.201/rpc"
plug_1 = ShellyPlug("http://192.168.1.201")

loop_time_interval = 30

def set_heater_power(level):
    # level = 0-100
    print(f"using power level: {level}")
    old_config = plug_1.switch.get_config()
    new_config = old_config.model_copy()
    new_config.initial_state = "on"
    new_auto_off_interval = max(1, int(level * 0.01 * loop_time_interval))
    time_off = loop_time_interval - new_auto_off_interval
    print(f"new on/off interval seconds: {new_auto_off_interval} (time on) / {time_off} (time off)")
    new_config.auto_off_delay = new_auto_off_interval
    plug_1.switch.set_config(new_config)

# Cycle period is 30 seconds
timespec1 = "*/30 * * * * *"

job = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=0, on=True),
)

# CREATE NEW scheduled tasks
req = ScheduleCreateRequest(
    id=1,
    params=ScheduleCreateParams(
        enable=True, timespec=timespec1, calls=[job.model_dump()]
    ),
)

response = post(device_rpc_url, json=req.model_dump())
schedule_create_1 = ScheduleCreateResponse(**response.json()["result"])


## set the DUTY CYCLE of the HOT PLATE output!
set_heater_power(75)
# new on/off interval seconds: 22 (time on) / 8 (time off)

### ENABLE OR DISABLE the power control settings
power_control_active = True
req = ScheduleUpdateRequest(
    id=1,
    params=ScheduleUpdateParams(
        id=2, enable=power_control_active, timespec=scheduled_tasks.jobs[0].timespec, calls=scheduled_tasks.jobs[0].calls
    ),
)
response = post(device_rpc_url, json=req.model_dump())
schedule_update = ScheduleUpdateResponse(**response.json()["result"])
