from pprint import pprint
from requests import post


from ishelly.components.switch import *
from ishelly.components.schedule import *
from ishelly.components.shelly import *

### DETAILS:
### This code is intended to control a Shelly PlugUS which is setup and running on your network.
### Mine is running at `http://192.168.1.201`.
### We create two scheduled events for the device: 1 for turning the light on, and 1 for turning the light off.


device_rpc_url = "http://192.168.1.201/rpc"

switch_id = 0
SECONDS_IN_HOUR = 3600
turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id, toggle_after=0, on=True),
)

turn_off = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id, toggle_after=0, on=False),
)


# CRON FORMAT: sec min hour days week weekend
# LIGHTS ON: 7AM
timespec_on = "0 0 7 * * *"

req = ScheduleCreateRequest(
    id=1,
    params=ScheduleCreateParams(
        enable=True, timespec=timespec_on, calls=[job_on.model_dump()]
    ),
)
response = post(device_rpc_url, json=req.model_dump())
schedule_create_1 = ScheduleCreateResponse(**response.json()["result"])

# LIGHTS OFF: 9PM
timespec_off = "0 0 21 * * *"

req = ScheduleCreateRequest(
    id=1,
    params=ScheduleCreateParams(
        enable=True, timespec=timespec_off, calls=[job_off.model_dump()]
    ),
)
response = post(device_rpc_url, json=req.model_dump())
schedule_create_1 = ScheduleCreateResponse(**response.json()["result"])