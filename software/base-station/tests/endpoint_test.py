import pytest
from fastapi.testclient import TestClient
from app import app

import os

os.environ["TEST"] = "1"

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_refresh():
    response = client.get("/refresh")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_pid_control():
    response = client.get("/pid_control")
    assert response.status_code == 200
    assert response.template.name == "pid_control.html"

def test_adjust_setpoint():
    data = {"new_setpoint": 50.0}
    response = client.post("/adjust_setpoint", json=data)
    assert response.status_code == 200
    assert "PID setpoint adjusted to 50.0" in response.json()["message"]

def test_update_integral():
    data = {"new_integral": 10.0}
    response = client.post("/update_integral", json=data)
    assert response.status_code == 200
    assert "PID integral setpoint updated to 10.0" in response.json()["message"]

def test_get_setpoint():
    response = client.get("/get_setpoint")
    assert response.status_code == 200
    assert "pid_1" in response.json()

def test_discover_devices():
    response = client.get("/discover_devices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_schedules():
    response = client.get("/list_schedules")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_outlet_detail():
    device_url = "test_device_url"
    response = client.get(f"/outlet_detail/{device_url}")
    assert response.status_code == 200
    assert response.template.name == "outlet_detail.html"
    assert response.context["device_url"] == device_url
