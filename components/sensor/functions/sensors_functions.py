import asyncio
import logging
import random
from datetime import datetime

import httpx

from controller.schemas.request import SensorData


class Sensor:
    # Class level constants
    PAYLOAD_MIN = 1
    PAYLOAD_MAX = 100

    def __init__(self, messages_per_second=300, logger=None,
                 controller_endpoint="http://localhost:8000/api/v1/controller/send_request"):
        self.sensor_count = 8
        self.messages_per_second = messages_per_second
        self.logger = logger or logging.getLogger()
        self.controller_endpoint = controller_endpoint

    async def generate_sensor_data(self, iterations: int = None):
        while iterations is None or iterations > 0:
            # self.logger.info(f'Iterations left: {iterations}')
            try:
                # Generate sensor reading
                payload = random.randint(self.PAYLOAD_MIN, self.PAYLOAD_MAX)

                # Format sensor reading
                data = SensorData(datetime=datetime.now().replace(microsecond=0).isoformat(), payload=payload)
                headers = {'Content-Type': 'application/json'}
                async with httpx.AsyncClient() as client:
                    request = await client.post(self.controller_endpoint, json=data.model_dump(mode='json'),
                                                headers=headers)
                    if request.status_code == 200:
                        self.logger.debug("Request successful!")
                    else:
                        self.logger.warning("Request unsuccessful.")
                # ...and wait
                await asyncio.sleep(1 / self.messages_per_second)

            except httpx.ConnectError:
                self.logger.warning("Connection error, retrying...")
                await asyncio.sleep(5)
            finally:
                if iterations is not None:
                    iterations -= 1
