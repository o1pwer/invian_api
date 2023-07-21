from datetime import datetime

from fastapi import APIRouter

from controller.main import app
from controller.schemas.request import SensorData
from controller.schemas.response import ControllerDecision

controller_router = APIRouter()

@app.post("controller/send_request", response_model=ControllerDecision)
async def recieve_request(data: SensorData):
    status = "down" if data.payload < 50 else "up"
    return ControllerDecision(datetime=datetime.now(), status=status)
