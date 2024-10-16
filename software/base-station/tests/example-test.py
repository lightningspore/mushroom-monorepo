import requests

# Example request data
request_data = {
    "device_url": "10.0.0.181",
    "schedule_id": 1,
    "switch_id": 0,
    "toggle_after_seconds": 32,
    "timespec": None
}

# Send the POST request
response = requests.post("https://80637d5c8ef5d1c191b3c04811023b28.balena-devices.com/update_schedule", json=request_data)

# Print the response
print(response.json())
