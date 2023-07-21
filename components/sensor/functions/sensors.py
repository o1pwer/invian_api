import asyncio
import random
from datetime import datetime

# Total sensors
SENSOR_COUNT = 8

# Messages per second from 1 sensor
MESSAGES_PER_SECOND = 300

# Range of indications
PAYLOAD_MIN = 1
PAYLOAD_MAX = 100

async def generate_sensor_data(sensor_id):
    while True:
        payload = random.randint(PAYLOAD_MIN, PAYLOAD_MAX)
        message = {
            "datetime": datetime.now().replace(microsecond=0).isoformat(),
            "payload": payload,
            "sensor_id": sensor_id,
        }
        print(message)
        await asyncio.sleep(1 / MESSAGES_PER_SECOND)

def run_sensor_tasks():
    return [generate_sensor_data(i) for i in range(SENSOR_COUNT)]