import random
from datetime import datetime


async def immitate_sensor_reading():
    reading = random.randint(0, 100)
    return {"datetime": datetime.now(), "payload": reading}