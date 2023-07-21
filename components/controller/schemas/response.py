from datetime import datetime

from pydantic import BaseModel


class ControllerDecision(BaseModel):
    datetime: datetime
    status: str


class Status(BaseModel):
    start: datetime
    end: datetime
    status: str


class ControllerHistory(BaseModel):
    start: datetime
    end: datetime
    status: str
