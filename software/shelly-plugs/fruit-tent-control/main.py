from pprint import pprint
from requests import post


from ishelly.components.switch import *
from ishelly.components.schedule import *
from ishelly.components.shelly import *
from ishelly.client import ShellyPlug, Shelly2PM, ShellyPro4PM

SECONDS_IN_HOUR = 3600

### DETAILS:
### This code is intended to control 2 Shelly2PM devices which are setup and running on your network.
### This code assumes you have a grow tent which has a light, a fan, and a humidifier.
### Events to be created:
### 1. Light control for Shelly2PM #1
### 2. Fan control for Shelly2PM #1
### 3. Humidifier control for Shelly2PM #2
### 4. NOT YET USED for Shelly2PM #2

# Initialize the Shelly Client Object
plug_1 = Shelly2PM("http://10.0.0.109")
plug_2 = Shelly2PM("http://10.0.0.186")
plug_pro = ShellyPro4PM("http://192.168.1.125")
plug_us = ShellyPlug("http://10.0.0.181")


# Define outlet ids
humidifier_switch_id = 0
exhaust_fan_switch_id = 2
light_switch_id = 3



#### CONFIGURE SHELLY 2PM #1 ####

#-#-#-#-#-#- LIGHT CONTROL START #-#-#-#-#-#-#
switch_id_light = 0
config = plug_1.switch[switch_id_light].get_config()
config.name = "Tent Light"
plug_1.switch[switch_id_light].set_config(config)

# CRON FORMAT: sec min hour days week weekend
# LIGHTS ON: 7AM
timespec_on = "0 0 7 * * *"

turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id_light, toggle_after=0, on=True),
)

plug_1.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])

# LIGHTS OFF: 9PM
timespec_off = "0 0 21 * * *"


turn_off = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id_light, toggle_after=0, on=False),
)

plug_1.schedule.create(enable=True, timespec=timespec_off, calls=[turn_off])
#-#-#-#-#-#- LIGHT CONTROL END #-#-#-#-#-#-#

#-#-#-#-#-#- FAN CONTROL START #-#-#-#-#-#-#
switch_id_fan = 1
config = plug_1.switch[switch_id_fan].get_config()
config.name = "Tent Fan"
plug_1.switch[switch_id_fan].set_config(config)

timespec_on = "0 */20 * * * *"
turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id_fan, toggle_after=120, on=True),
)

plug_1.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])
#-#-#-#-#-#- FAN CONTROL END #-#-#-#-#-#-#


#### CONFIGURE SHELLY 2PM #2 ####

#-#-#-#-#-#- HUMIDIFIER CONTROL START #-#-#-#-#-#-#
switch_id_humidifier = 0

config = plug_2.switch[switch_id_humidifier].get_config()
config.name = "Tent Humidifier"
plug_2.switch[switch_id_humidifier].set_config(config)


timespec_on = "0 */2 * * * *"
turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=switch_id_humidifier, toggle_after=40, on=True),
)

plug_2.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])
#-#-#-#-#-#- HUMIDIFIER CONTROL END #-#-#-#-#-#-#

# New scheduled task for plug_us
switch_id_plug_us = 0
config = plug_us.switch.get_config()
config.name = "Humidifier"
plug_us.switch.set_config(config)

timespec_on = "0 */1 * * * *"
turn_on = SwitchSetRequest(
    id=1,
    params=SwitchSetParams(id=humidifier_switch_id, toggle_after=55, on=True),
)

plug_us.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])
plug_pro.schedule.create(enable=True, timespec=timespec_on, calls=[turn_on])

plug_pro.schedule.update(5, True, timespec_on, calls=[turn_on])
