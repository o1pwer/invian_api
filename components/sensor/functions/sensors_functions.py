import asyncio
import logging
import random
from datetime import datetime
from urllib.parse import urlparse

import httpx
import pika

from invian_shared.shared_schemas import SensorData


class Sensor:
    """
        This class represents a Sensor which generates and sends data to a specified endpoint.

        Attributes:
            PAYLOAD_MIN (int): The minimum value that the sensor can generate.
            PAYLOAD_MAX (int): The maximum value that the sensor can generate.
            sensor_count (int): The number of sensors that are being simulated.
            messages_per_second (int): The rate at which each sensor generates data.
            logger (logging.Logger): A logger instance for logging information.
            controller_endpoint (str): The URL endpoint to which sensor data is sent.

        Methods:
            generate_sensor_data(iterations: Optional[int] = None) -> None:
                Simulate sensor data generation and send data to the specified endpoint.

            _is_valid_url(url: str) -> bool:
                Check if a given string is a valid URL.
        """
    # Class level constants
    PAYLOAD_MIN = 1
    PAYLOAD_MAX = 100

    def __init__(self, messages_per_second=300, logger=None,
                 controller_endpoint="http://controller:8000/api/v1/controller/data"):
        if messages_per_second <= 0:
            raise ValueError("messages_per_second must be a positive number")
        if not self._is_valid_url(controller_endpoint):
            raise ValueError("controller_endpoint must be a valid URL")
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
            except Exception as exc:
                self.logger.warning(f"Unknown error, retrying...\nDetails: {exc}")
                await asyncio.sleep(5)
            finally:
                if iterations is not None:
                    iterations -= 1


    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
