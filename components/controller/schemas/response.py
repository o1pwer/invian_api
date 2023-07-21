from pydantic import BaseModel
from datetime import datetime

class ControllerDecision(BaseModel):
    datetime: datetime
    status: str