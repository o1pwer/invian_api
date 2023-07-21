import asyncio
from datetime import datetime

from components.sensor.functions.sensors import SENSOR_COUNT

STATUS_THRESHOLD = 50

# Типа БД
latest_data = {i: None for i in range(SENSOR_COUNT)}


async def process_sensor_data(sensor_id, data):
    # Сохраняем данные в нашу БД
    latest_data[sensor_id] = data


async def make_decision():
    while True:
        # Подсчитаем, сколько нам пришло показаний с сенсоров...
        total_payload = sum(data["payload"] for data in latest_data.values() if data is not None)
        average_payload = total_payload / len(latest_data)

        # ... если их слишком много, то статус будет "down".
        status = "up" if average_payload > STATUS_THRESHOLD else "down"

        # Создадим ответ...
        message = {
            "datetime": datetime.now().isoformat(),
            "status": status,
        }

        # ...и пока просто его запринтим.
        print(message)

        # Ждем следующего решения.
        await asyncio.sleep(5)
