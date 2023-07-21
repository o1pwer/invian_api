import asyncio
import random
from datetime import datetime

import httpx

# Всего сенсоров
from controller.schemas.request import SensorData

SENSOR_COUNT = 8

# Число сообщений в секунду от 1 сенсора
MESSAGES_PER_SECOND = 300

# Диапазон показаний счетчика
PAYLOAD_MIN = 1
PAYLOAD_MAX = 100

# Эндпоинт, куда мы посылаем запросы
CONTROLLER_ENDPOINT = "http://localhost:8000/api/v1/controller/send_request"


async def generate_sensor_data():
    while True:
        try:
            # Генерируем показания счетчика
            payload = random.randint(PAYLOAD_MIN, PAYLOAD_MAX)

            # Форматируем показания счетчика
            data = SensorData(datetime=datetime.now().replace(microsecond=0).isoformat(), payload=payload)
            headers = {'Content-Type': 'application/json'}
            async with httpx.AsyncClient() as client:
                await client.post(CONTROLLER_ENDPOINT, json=data.model_dump(mode='json'), headers=headers)

            # ...и ждем
            await asyncio.sleep(1 / MESSAGES_PER_SECOND)
        except httpx.ConnectError:
            print("Connection error, retrying...")
            await asyncio.sleep(5)  # Ждем 5 сек перед повторным подключением
