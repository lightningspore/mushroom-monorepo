from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates

from pydantic import BaseModel
from typing import List, Optional

from ishelly.client import ShellyDiscovery
from ishelly.client import ShellyPro4PM
from ishelly.client import SwitchSetRequest, SwitchSetParams

import socket
import ipaddress
import asyncio

from pid.run_pid import pid, waiting_loop


templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.state.devices = {}

def get_local_cidr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    cidr = ipaddress.ip_network(f'{ip}/24', strict=False)
    return str(cidr)

def device_discovery():
    cidr = get_local_cidr()
    discovery = ShellyDiscovery(cidr)
    devices = [ url.rstrip("/rpc") for url in discovery.discover_devices() ] 
    return devices

@app.on_event("startup")
async def startup_event():
    devices = device_discovery()
    app.state.devices = devices
    asyncio.create_task(waiting_loop())

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/refresh")
def refresh():
    devices = device_discovery()
    app.state.devices = devices
    return app.state.devices

@app.post("/adjust_setpoint")
def adjust_setpoint(new_setpoint: float):
    """
    Adjust the target setpoint of the PID loop.
    """
    pid.setpoint = new_setpoint
    return {"message": f"PID setpoint adjusted to {new_setpoint}"}


@app.post("/update_integral")
def update_integral(new_integral: float):
    """
    Update the current integral setpoint of the PID controller.
    """
    pid.set_auto_mode(False)
    pid.set_auto_mode(True, last_output=new_integral)
    return {"message": f"PID integral setpoint updated to {new_integral}"}

@app.get("/discover_devices")
def discover_devices():
    return app.state.devices

@app.get("/list_schedules")
def list_schedules():
    schedules = {}
    for device_url in app.state.devices:
        plug_pro = ShellyPro4PM(device_url)
        current_schedule = plug_pro.schedule.list()
        schedules[device_url] = [str(task) for task in current_schedule.jobs]
    return schedules

class ScheduleUpdateRequest(BaseModel):
    device_url: str
    schedule_id: int
    switch_id: int
    toggle_after_seconds: int
    timespec: Optional[str] = None
    next_state: bool

@app.post("/update_schedule")
def update_schedule(request: ScheduleUpdateRequest):
    plug_pro = ShellyPro4PM(f"http://{request.device_url}")

    turn_on = SwitchSetRequest(
        id=1,
        params=SwitchSetParams(id=request.switch_id, toggle_after=request.toggle_after_seconds, on=request.next_state),
    )

    plug_pro.schedule.update(request.schedule_id, request.timespec, calls=[turn_on])
    return {"message": "Schedule updated successfully"}



@app.get("/list_schedules/{device_url}")
def list_schedules_for_device(device_url: str):
    plug_pro = ShellyPro4PM(f"http://{device_url}")
    current_schedule = plug_pro.schedule.list()
    schedules = [{"id": job.id, "timespec": job.timespec, "calls": [str(call) for call in job.calls]} for job in current_schedule.jobs]
    return schedules




@app.get("/outlet_detail/{device_url}")
def outlet_detail(device_url: str, request: Request):
    return templates.TemplateResponse("outlet_detail.html", {"request": request, "device_url": device_url})
