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


plug_1 = ShellyPlug("http://10.0.0.238")

switch_id = 0
SECONDS_IN_HOUR = 3600


# CRON FORMAT: sec min hour days week weekend
# EVERY 3 minutes, turn on for 1 minute
timespec_on = "0 */3 * * * *"

turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id, toggle_after=60, on=True),
)

plug_1.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])
