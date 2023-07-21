from datetime import datetime, timedelta
from typing import List

from controller.schemas.request import SensorData
from controller.schemas.response import Status, ControllerDecision

STATUS_THRESHOLD = 50

# Список для хранения данных от датчиков
latest_data = []
history = []
last_decision_time = datetime.now()


async def process_request(data: SensorData) -> ControllerDecision:
    global last_decision_time
    data.datetime = datetime.fromisoformat(data.datetime)
    # Добавляем полученные данные в список latest_data
    latest_data.append(data.payload)

    # Проверяем, прошло ли 5 минут с момента последнего решения
    now = datetime.now().replace(microsecond=0)
    now_str = now.isoformat()
    if now - last_decision_time < timedelta(minutes=5):
        # Если нет, то новое решение пока не принимаем
        return

    last_decision_time_str = last_decision_time.isoformat()

    # Принимаем решение на основе последних данных
    total_payload = sum(latest_data)
    average_payload = total_payload / len(latest_data)

    status = "up" if average_payload > STATUS_THRESHOLD else "down"

    # Обновляем историю
    if history and history[-1].status == status:
        # Если статус такой же, как и последний, просто обновляем время окончания
        history[-1].end = now_str
    else:
        # Если статус отличается, добавляем новую запись в историю
        history.append(Status(start=last_decision_time_str, end=now_str, status=status))

    last_decision_time = now

    # Очищаем список latest_data, так как мы уже обработали эти данные
    latest_data.clear()

    return ControllerDecision(datetime=now, status=status)

def format_history(history: List[Status]) -> List[str]:
    # Форматирование истории как списка.
    formatted_history = [
        f"[{status.start.strftime('%H:%M')} - {status.end.strftime('%H:%M')} {status.status.upper()}]"
        for status in history
    ]
    return formatted_history


def format_history_as_string(history: List[Status]) -> str:
    # Форматирование истории как строки.
    formatted_history = []
    for record in history:
        formatted = f"[{record.start.strftime('%H:%M')} - {record.end.strftime('%H:%M')} {record.status.upper()}]"
        formatted_history.append(formatted)
    return ', '.join(formatted_history)
