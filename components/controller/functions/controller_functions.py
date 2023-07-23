import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List

from controller.exceptions.controller_exceptions import BadPayloadException
from controller.schemas.request import SensorData
from controller.schemas.response import Status, ControllerDecision
from utils.network import tcp_client


def get_current_time_without_microseconds():
    return datetime.now().replace(microsecond=0)


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Controller(metaclass=Singleton):

    def __init__(self, status_threshold=50, log_level=logging.DEBUG, min_payload=1, max_payload=100,
                 decision_interval_seconds=5):
        self.status_threshold = status_threshold
        self._init_state(log_level)
        self.min_payload = min_payload
        self.max_payload = max_payload
        self.decision_interval_seconds = decision_interval_seconds

    def _init_state(self, log_level: int):
        self.latest_data = []
        self.history = []
        self.last_decision_time = get_current_time_without_microseconds()
        self.previous_status = None
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

    def reset(self):
        self._init_state(logging.DEBUG)

    def _validate_payload(self, payload: int):
        if payload > self.max_payload:
            raise BadPayloadException(f"Received unrealistically high payload: {payload}. Ignoring.")
        if payload < self.min_payload:
            raise BadPayloadException(f"Received unrealistically low payload: {payload}. Ignoring.")
        # raise BadPayloadException("Received good payload!")

    async def process_request(self, data: SensorData) -> ControllerDecision | None:
        self.logger.debug('Processing request...')
        async with self.lock:
            self.logger.debug('Lock acquired.')
            self._validate_payload(data.payload)
            data.datetime = datetime.fromisoformat(data.datetime)

            self.latest_data.append(data.payload)

            now = get_current_time_without_microseconds()
            time_difference = now - self.last_decision_time
            self.logger.debug(
                f"Now: {now}, Last decision time: {self.last_decision_time}, Time difference: {time_difference}")

            now_str = now.isoformat()
            self.logger.debug('Checking decision time...')
            if time_difference < timedelta(seconds=self.decision_interval_seconds):
                self.logger.debug('Returning early due to decision time.')
                # self.latest_data.clear()
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

            if self.history and self.history[-1].status == status:
                self.history[-1].end = now
            else:
                self.history.append(
                    Status(start=datetime.fromisoformat(last_decision_time_str), end=datetime.fromisoformat(now_str),
                           status=status))

            self.last_decision_time = now

            self.latest_data.clear()
            self.previous_status = status
            self.logger.debug('Finished processing request.')
            return ControllerDecision(datetime=now, status=status)

    def _format_history(self, history: List[Status]) -> List[str]:
        return [f"[{status.start.strftime('%H:%M:%S')} - {status.end.strftime('%H:%M:%S')} {status.status.upper()}]" for status in history]

    def _format_history_as_string(self, history: List[Status]) -> str:
        formatted_history = [
            f"[{record.start.strftime('%H:%M:%S')} - {record.end.strftime('%H:%M:%S')} {record.status.upper()}]" for
            record in history]
        return ', '.join(formatted_history)

    def get_history(self) -> List[str]:
        return self._format_history(self.history)

    def get_history_as_string(self) -> str:
        return self._format_history_as_string(self.history)


def get_controller():
    return Controller()
