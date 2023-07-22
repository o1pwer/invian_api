from typing import List, Optional

from fastapi import APIRouter

from controller.functions.controller_functions import format_history, format_history_as_string, process_request, history
from controller.schemas.request import SensorData
from controller.schemas.response import ControllerDecision

controller_router = APIRouter()


@controller_router.post("/controller/send_request", response_model=Optional[ControllerDecision])
async def recieve_request(data: SensorData):
    # print(f"Data: {data}")
    # print(f"Type of data: {type(data)}")
    response = await process_request(data)
    if response:
        return response


@controller_router.get("/controller/history", response_model=List[str])
async def get_history():
    return format_history(history)


@controller_router.get("/controller/history_string", response_model=str)
async def get_history_string():
    return format_history_as_string(history)
