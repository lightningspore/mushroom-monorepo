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

plug_1 = ShellyPlug("http://192.168.1.201")

#### CONFIGURE SHELLY PLUG US #1 ####
#-#-#-#-#-#- LIGHT CONTROL START #-#-#-#-#-#-#

switch_id_light = 0

config = plug_1.switch[switch_id_light].get_config()
config.name = "Light"
plug_1.switch[switch_id_light].set_config(config)


pprint(plug_1.schedule.list().jobs)

# CRON FORMAT: sec min hour days week weekend
# LIGHTS ON: 7AM
timespec_on = "0 0 7 * * 0,1,2,3,4,5,6"

turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id_light, toggle_after=None, on=True),
)

plug_1.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])

# LIGHTS OFF: 9PM
timespec_off = "0 0 22 * * 0,1,2,3,4,5,6"

timespec_off = "0 49 22 * * 0,1,2,3,4,5,6"
timespec_off = "10 53 22 * * *"


turn_off = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id_light, toggle_after=None, on=False),
)

plug_1.schedule.create(enable=True, timespec=timespec_off, calls=[turn_off])
#-#-#-#-#-#- LIGHT CONTROL END #-#-#-#-#-#-#

plug_pro.schedule.update(3, True, timespec_off, calls=[turn_off])

plug_pro.schedule.update(2, True, timespec_on, calls=[turn_on])
