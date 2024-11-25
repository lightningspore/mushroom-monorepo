import os
from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from contextlib import asynccontextmanager


from pydantic import BaseModel
from typing import List, Optional

from ishelly.client import ShellyDiscovery
from ishelly.client import ShellyPro4PM
from ishelly.client import SwitchSetRequest, SwitchSetParams

import socket
import ipaddress
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from pid.run_pid import pid, waiting_loop


logger = logging.getLogger()

# Console Logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# File Logger
log_file = "app.log"
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
file_handler.setFormatter(log_formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Searching for devices on network!")
    devices = device_discovery()
    app.state.devices = devices
    logger.info("device discovery completed...")
    if os.getenv("TEST") == "1":
        logger.info("not running loop in test mode!")
    asyncio.create_task(waiting_loop())
    logger.info("PID Control loop started!")
    yield


app = FastAPI(lifespan=lifespan)

app.state.devices = {}


def get_local_cidr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    cidr = ipaddress.ip_network(f"{ip}/24", strict=False)
    return str(cidr)


def device_discovery():
    cidr = get_local_cidr()
    discovery = ShellyDiscovery(cidr)
    devices = [str(url).rstrip("/rpc") for url in discovery.discover_devices()]
    return devices


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/refresh")
async def refresh():
    devices = device_discovery()
    app.state.devices = devices
    return app.state.devices


@app.get("/pid_control", response_class=HTMLResponse)
async def pid_control(request: Request):
    logger.debug("ENDPOINT: /pid_control")
    # return templates.TemplateResponse("pid_control.html", {"request": request})
    return templates.TemplateResponse(request, "pid_control.html", {"request": request})



class UpdateSetpointRequest(BaseModel):
    new_setpoint: float


@app.post("/adjust_setpoint")
async def adjust_setpoint(request: UpdateSetpointRequest):
    """
    Adjust the target setpoint of the PID loop.
    """
    try:
        new_setpoint = request.new_setpoint
        logger.info(f"New Setpoint: {new_setpoint}")
        pid.setpoint = new_setpoint
        return {"message": f"PID setpoint adjusted to {new_setpoint}"}
    except Exception as e:
        logger.error(f"Error adjusting setpoint: {e}")
        return {"error": str(e)}


class UpdateIntegralRequest(BaseModel):
    new_integral: float


@app.post("/update_integral")
async def update_integral(request: UpdateIntegralRequest):
    """
    Update the current integral setpoint of the PID controller.
    """
    try:
        new_integral = request.new_integral
        logger.info(f"New integral: {new_integral}")
        pid.set_auto_mode(False)
        pid.set_auto_mode(True, last_output=new_integral)
        return {"message": f"PID integral setpoint updated to {new_integral}"}
    except Exception as e:
        logger.error(f"Error adjusting integral: {e}")
        return {"error": str(e)}


@app.get("/get_setpoint")
async def get_setpoint():
    """
    Get the current setpoint of the PID controller.
    """
    try:
        current_setpoint = pid.setpoint
        return {"pid_1": current_setpoint}
    except Exception as e:
        logger.error(f"Error getting setpoint: {e}")
        return {"error": str(e)}


@app.get("/discover_devices")
async def discover_devices():
    return app.state.devices


@app.get("/list_schedules")
async def list_schedules():
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
        params=SwitchSetParams(
            id=request.switch_id,
            toggle_after=request.toggle_after_seconds,
            on=request.next_state,
        ),
    )

    plug_pro.schedule.update(request.schedule_id, request.timespec, calls=[turn_on])
    return {"message": "Schedule updated successfully"}


@app.get("/list_schedules/{device_url}")
def list_schedules_for_device(device_url: str):
    plug_pro = ShellyPro4PM(f"http://{device_url}")
    current_schedule = plug_pro.schedule.list()
    schedules = [
        {
            "id": job.id,
            "timespec": job.timespec,
            "calls": [str(call) for call in job.calls],
        }
        for job in current_schedule.jobs
    ]
    return schedules


@app.get("/outlet_detail/{device_url}")
def outlet_detail(device_url: str, request: Request):
    return templates.TemplateResponse(
        request, "outlet_detail.html", {"request": request, "device_url": device_url}
    )
