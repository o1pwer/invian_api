import asyncio
import logging

from sensor.functions.sensors_functions import Sensor

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Сенсоры ничего не знают о состоянии других объектов, они просто отправляют свои показания и все.


if __name__ == '__main__':
    sensor = Sensor(logger=logger)
    logging.info('We are sensors and we are starting!!!')
    tasks = [sensor.generate_sensor_data() for _ in range(sensor.sensor_count)]
    asyncio.run(asyncio.wait(tasks))
