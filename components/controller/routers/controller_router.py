from typing import List, Optional

from fastapi import APIRouter

from controller.functions.controller_functions import Controller
from controller.schemas.request import SensorData
from controller.schemas.response import ControllerDecision

controller = Controller()
controller_router = APIRouter()


@controller_router.post("/controller/send_request", response_model=Optional[ControllerDecision])
async def recieve_request(data: SensorData):
    response = await controller.process_request(data)
    if response:
        return response


@controller_router.get("/controller/history", response_model=List[str])
async def get_history():
    return controller.get_history()


@controller_router.get("/controller/history_string", response_model=str)
async def get_history_string():
    return controller.get_history_as_string()