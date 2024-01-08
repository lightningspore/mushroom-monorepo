from pprint import pprint
from requests import post


from ishelly.components.switch import *
from ishelly.components.schedule import *
from ishelly.components.shelly import *
from ishelly.client import ShellyPlug

### DETAILS:
### This code is intended to control a Shelly PlugUS which is setup and running on your network.
### Mine is running at `http://192.168.1.201`.
### We create two scheduled events for the device: 1 for turning the light on, and 1 for turning the light off.


device_rpc_url = "http://192.168.1.201/rpc"

switch_id = 0
SECONDS_IN_HOUR = 3600


# CRON FORMAT: sec min hour days week weekend
# LIGHTS ON: 7AM
timespec_on = "0 0 7 * * *"

turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id, toggle_after=0, on=True),
)

plug_1.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])

# LIGHTS OFF: 9PM
timespec_off = "0 0 21 * * *"


turn_off = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id, toggle_after=0, on=False),
)

plug_1.schedule.create(enable=True, timespec=timespec_off, calls=[turn_off])