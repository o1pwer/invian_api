from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    datetime: datetime
    payload: int
