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

def run_query():
    query = os.getenv("BASE_QUERY")

    query = query.rstrip().lstrip()

    # start_time = '2024-10-06T00:00:00Z'
    # end_time = '2024-10-06T02:00:00Z'
    start_time = (datetime.now(timezone.utc)-timedelta(hours=1)).replace(microsecond=0).isoformat()
    end_time = (datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    step = '1m'

    import code
    # code.interact(local=locals())

    results = query_grafana_cloud_prometheus(query, start_time, end_time, step)

    target_data = results[0]
    print(f"timestamp range: {target_data['values'][0][0]} - {target_data['values'][-1][0]}")


    pprint(target_data["values"])
    range_data_list = [ float(x[1]) for x in target_data["values"] ]
    min_val = round(min(range_data_list),1)
    max_val = round(max(range_data_list),1)
    mean_val = round(mean(range_data_list),1)

    print(f"Humidity Calculation (Last Hour)")
    print(f"Mean -> {mean_val}... Min -> {min_val}... Max -> {max_val}")


    return mean_val


if __name__ == "__main__":
    r = run_query()
    print(f"got result: {r}")