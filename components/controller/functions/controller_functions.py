from datetime import datetime, timedelta
from typing import List

from controller.schemas.request import SensorData
from controller.schemas.response import Status, ControllerDecision
import socket
import json
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
STATUS_THRESHOLD = 50

# Здесь переменные для хранения данных от датчиков
latest_data = []
history = []
last_decision_time = datetime.now()
history_append_time = datetime.now()
start_time = datetime.now()

# Предыдущий статус манипулятора
previous_status = None


async def process_request(data: SensorData) -> ControllerDecision:
    global last_decision_time, previous_status
    data.datetime = datetime.fromisoformat(data.datetime)

    # Добавляем полученные данные в список latest_data
    latest_data.append(data.payload)

    # Проверяем, прошло ли 5 секунд с момента последнего решения
    now = datetime.now().replace(microsecond=0)
    now_str = now.isoformat()
    if now - last_decision_time < timedelta(seconds=5):
        # Если нет, то новое решение пока не принимаем
        return
    logger.info("Начало принятия решения.")
    last_decision_time_str = last_decision_time.isoformat()

    # Принимаем решение на основе последних данных
    total_payload = sum(latest_data)
    average_payload = total_payload / len(latest_data)

    status = "up" if average_payload > STATUS_THRESHOLD else "down"
    logger.info(f"Статус: {status}")
    if status != previous_status:
        print(f"Статус изменился: {previous_status} -> {status}")
        decision = ControllerDecision(datetime=now, status=status)
        logger.info(f"Принято решение: {decision}")
        tcp_client(json.dumps(decision.model_dump(mode='json')))
    previous_status = status

    # Обновляем историю
    if history and history[-1].status == status:
        # Если статус такой же, как и последний, просто обновляем время окончания
        history[-1].end = now
    else:
        # Если статус изменился, добавляем новую запись в историю
        history.append(Status(start=datetime.fromisoformat(last_decision_time_str),
                              end=datetime.fromisoformat(now_str),
                              status=status))

    last_decision_time = now

    # Очищаем список latest_data, так как мы уже обработали эти данные
    latest_data.clear()
    decision = ControllerDecision(datetime=now, status=status)
    return decision

def format_history(history: List[Status]) -> List[str]:
    # Форматируем историю как список строк
    return [
        f"[{status.start.strftime('%H:%M:%S')} - {status.end.strftime('%H:%M:%S')} {status.status.upper()}]"
        for status in history
    ]

def format_history_as_string(history: List[Status]) -> str:
    # Форматируем историю как одну строку
    formatted_history = []
    for record in history:
        formatted = f"[{record.start.strftime('%H:%M:%S')} - {record.end.strftime('%H:%M:%S')} {record.status.upper()}]"
        formatted_history.append(formatted)
    return ', '.join(formatted_history)


def tcp_client(message: str):
    # Создаем сокет TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Подключаем сокет к адресу и порту сервера
    server_address = ('localhost', 55555)
    print(f"Подключаемся к {server_address[0]} порт {server_address[1]}")
    try:
        client_socket.connect(server_address)
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

    try:
        # Отправляем данные
        message += "\n"  # добавляем символ новой строки в конец
        print(f"Отправляем {message}")
        client_socket.sendall(message.encode())
    finally:
        print("Закрываем сокет")
        client_socket.close()