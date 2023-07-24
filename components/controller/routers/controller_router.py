import logging
from typing import Optional, List

from fastapi import APIRouter, Depends
from fastapi import FastAPI

from controller.functions.controller_functions import Controller
from controller.schemas.response import ControllerDecision
from invian_shared.shared_exceptions import BadPayloadException
from invian_shared.shared_schemas import SensorData

logger = logging.getLogger()


def get_controller(app: FastAPI = Depends()):
    return app.state.controller


controller_router = APIRouter()


@controller_router.post("/controller/data", response_model=Optional[ControllerDecision])
async def recieve_request(data: SensorData):
    controller = Controller()
    try:
        response = await controller.process_request(data)
        if response:
            return response
    except BadPayloadException as exc:
        logger.warning(f"Received bad payload.\nDetails: {exc}")

@controller_router.get("/controller/history", response_model=List[str])
async def get_history():
    controller = Controller()
    return controller.get_history()

@controller_router.get("/controller/history_string", response_model=str)
async def get_history_string():
    controller = Controller()
    return controller.get_history_as_string()