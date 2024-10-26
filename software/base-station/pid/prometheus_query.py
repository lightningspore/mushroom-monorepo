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

def get_latest_value(query):
    prometheus_url = os.getenv("PROM_URL") + "/api/v1/query"
    params = {
        'query': query
    }
    response = requests.get(prometheus_url, auth=auth, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['data']['resultType'] == 'vector':
            return data['data']['result'][0]['value'][1]
        else:
            print("Error: Unexpected result type")
            return None
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def run_query():
    # ENV example
    # query = 
    query = os.getenv("BASE_QUERY")

    # target_sensor = os.getenv("QUERY_FILTER")

    # # ENV example! Dont include the single quotes in the ENV var
    # # filter = '"job="spore-sensors",location="spore-lab",instance="10.0.0.73:6969",name="SCD41 Humidity"'

    # # TODO
    # # TODO!!!! START HERE

    # query = f"""
    # avg_over_time(esphome_sensor_value{query}[5m])
    # """

    query = query.rstrip().lstrip()

    # start_time = '2024-10-06T00:00:00Z'
    # end_time = '2024-10-06T02:00:00Z'
    # start_time = (datetime.now(timezone.utc)-timedelta(minutes=20)).replace(microsecond=0).isoformat()
    # end_time = (datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    # step = '1m'

    import code
    # code.interact(local=locals())

    # results = query_grafana_cloud_prometheus(query, start_time, end_time, step)
    result = get_latest_value(query)
    return round(float(result),1)


if __name__ == "__main__":
    r = run_query()
    print(f"got result: {r}")