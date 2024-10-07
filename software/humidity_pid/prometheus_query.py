import os
import requests
import json
from requests.auth import HTTPBasicAuth
from urllib.parse import quote_plus
from datetime import datetime, timedelta, timezone
from statistics import mean
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
username = os.getenv("GRAFANA_USERNAME")
password = os.getenv("GRAFANA_PASSWORD")
auth = HTTPBasicAuth(username, password)

def query_grafana_cloud_prometheus(query, start_time, end_time, step):
    prometheus_url = os.getenv("PROM_URL") + "/api/v1/query_range"

    params = {
        'query': query,
        'start': start_time,
        'end': end_time,
        'step': step
    }
    response = requests.get(prometheus_url, auth=auth, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['data']['result']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
# query = '''

# '''
query = os.getenv("BASE_QUERY")

query = query.rstrip().lstrip()

# start_time = '2024-10-06T00:00:00Z'
# end_time = '2024-10-06T02:00:00Z'
start_time = (datetime.now(timezone.utc)-timedelta(hours=1)).replace(microsecond=0).isoformat()
end_time = (datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
step = '1m'

import code
code.interact(local=locals())

results = query_grafana_cloud_prometheus(query, start_time, end_time, step)

target_data = results[0]
print(f"timestamp range: {target_data["values"][0][0]} - {target_data["values"][-1][0]}")


pprint(target_data["values"])
range_data_list = [ float(x[1]) for x in target_data["values"] ]
min_val = round(min(range_data_list),1)
max_val = round(max(range_data_list),1)
mean_val = round(mean(range_data_list),1)

print(f"Humidity Calculation (Last Hour)")
print(f"Mean -> {mean_val}... Min -> {min_val}... Max -> {max_val}")


# How to control PID?
sensor_setpoint = 86
sensor_maxset_limit = 90
sensor_minset_limit = 80

# minimum has to be above minimum setpoint
# maximum has to be below maximum setpoint
# mean tracking the target setpoint

current_powerset = 0.7
powerset_changeval = 0.01

# the power output is a value between 0-1
# the power can only be modified by powerset_changeval
# each period

# PID controller to keep sensor value within specified range
# Kp = 0
# Ki = 0
# Kd = 0
# error = mean_val - sensor_setpoint
# integral = integral + error
# derivative = error - previous_error
# output = Kp * error + Ki * integral + Kd * derivative
# previous_error = error

# # Adjust power output based on PID output
# if output > 0:
#     current_powerset = min(current_powerset + powerset_changeval, 1.0)
# else:
#     current_powerset = max(current_powerset - powerset_changeval, 0.0)

# # Ensure power output is within limits
# current_powerset = max(min(current_powerset, sensor_maxset_limit), sensor_minset_limit)

# # Set power output for humidity control system
# set_humidity_control_power(current_powerset)


if results:
    pass
    # print(json.dumps(results, indent=2))
else:
    print("No results returned.")