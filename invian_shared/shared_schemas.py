from pydantic import BaseModel


class SensorData(BaseModel):
    datetime: str
    payload: int
