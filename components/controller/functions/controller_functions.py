import asyncio
import json
import socket
from datetime import datetime, timedelta
from typing import List

import httpx

from controller.schemas.request import SensorData
from controller.schemas.response import Status, ControllerDecision
import logging
# Нужно накидать сюда смешных комментов.
# Прошу, не забудь. =)
def current_time():
    return datetime.now().replace(microsecond=0)

class Controller:
    def __init__(self, status_threshold=50, log_level=logging.DEBUG):
        self.status_threshold = status_threshold
        self.latest_data = []
        self.history = []
        self.last_decision_time = current_time()
        self.previous_status = None
        self.lock = asyncio.Lock()

        logging.basicConfig(format='%(asctime)s %(message)s', level=log_level, handlers=[logging.StreamHandler()])
        self.logger = logging.getLogger(__name__)

    async def process_request(self, data: SensorData) -> ControllerDecision:
        async with self.lock:
            data.datetime = datetime.fromisoformat(data.datetime)

            self.latest_data.append(data.payload)

            now = current_time()
            now_str = now.isoformat()
            if now - self.last_decision_time < timedelta(seconds=5):
                return

            self.logger.info("Начало принятия решения.")
            last_decision_time_str = self.last_decision_time.isoformat()

            total_payload = sum(self.latest_data)
            average_payload = total_payload / len(self.latest_data)

            status = "up" if average_payload > self.status_threshold else "down"
            self.logger.info(f"Статус: {status}")
            if status != self.previous_status:
                print(f"Статус изменился: {self.previous_status} -> {status}")
                decision = ControllerDecision(datetime=now, status=status)
                self.logger.info(f"Принято решение: {decision}")
                await tcp_client(json.dumps(decision.model_dump(mode='json')))

            self.previous_status = status

            if self.history and self.history[-1].status == status:
                self.history[-1].end = now
            else:
                self.history.append(Status(start=datetime.fromisoformat(last_decision_time_str), end=datetime.fromisoformat(now_str), status=status))

            self.last_decision_time = now

            self.latest_data.clear()

            return ControllerDecision(datetime=now, status=status)

    def _format_history(self, history: List[Status]) -> List[str]:
        return [f"[{status.start.strftime('%H:%M:%S')} - {status.end.strftime('%H:%M:%S')} {status.status.upper()}]" for status in history]

    def _format_history_as_string(self, history: List[Status]) -> str:
        formatted_history = [f"[{record.start.strftime('%H:%M:%S')} - {record.end.strftime('%H:%M:%S')} {record.status.upper()}]" for record in history]
        return ', '.join(formatted_history)

    def get_history(self) -> List[str]:
        return self._format_history(self.history)

    def get_history_as_string(self) -> str:
        return self._format_history_as_string(self.history)


async def tcp_client(message: str, server_address='localhost', server_port=8080):
    url = f"http://{server_address}:{server_port}/"
    print(f"Подключаемся к {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=message)
        except httpx.ConnectError:
            print("Не удалось подключиться к серверу")
            return
        print(f"Отправляем {message}")
        print("Закрываем сокет")