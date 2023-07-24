import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Union

from controller.schemas.response import Status, ControllerDecision
from invian_shared.shared_exceptions import BadPayloadException
from invian_shared.shared_schemas import SensorData
from invian_shared.utils.network import tcp_client


def get_current_time_without_microseconds():
    return datetime.now().replace(microsecond=0)


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Controller(metaclass=Singleton):
    """
    The Controller class processes sensor data and makes decisions based on it.
    It is implemented as a Singleton, ensuring only one instance is created.

    Attributes:
        status_threshold (int): The payload threshold at which the controller status changes.
        min_payload (int): The minimum value of payload that the controller considers valid.
        max_payload (int): The maximum value of payload that the controller considers valid.
        decision_interval_seconds (int): The time interval (in seconds) between each decision.
        latest_data (list): The list of latest payloads received.
        history (list): The history of statuses and their respective time intervals.
        last_decision_time (datetime): The time when the last decision was made.
        previous_status (str): The previous status of the controller.
        lock (asyncio.Lock): A lock to ensure thread safety.
        logger (logging.Logger): A logger instance for logging information.

    Methods:
        reset() -> None:
            Resets the controller's state.
        process_request(data: SensorData) -> ControllerDecision | None:
            Processes a request containing sensor data and makes a decision based on it.
            Returns the decision if a new one is made, or None otherwise.
        get_history() -> List[str]:
            Returns the history of statuses in a formatted manner.
        get_history_as_string() -> str:
            Returns the history of statuses as a string.
    """

    def __init__(self, status_threshold=50, log_level=logging.DEBUG, min_payload=1, max_payload=100,
                 decision_interval_seconds=5):
        # Initialize instance variables
        self.status_threshold = status_threshold
        self._init_state(log_level)
        self.min_payload = min_payload
        self.max_payload = max_payload
        self.decision_interval_seconds = decision_interval_seconds

    def _init_state(self, log_level: int):
        # Reset the state of the controller
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
        # Validate the payload value
        if payload > self.max_payload:
            raise BadPayloadException(f"Received unrealistically high payload: {payload}. Ignoring.")
        if payload < self.min_payload:
            raise BadPayloadException(f"Received unrealistically low payload: {payload}. Ignoring.")

    async def process_request(self, data: SensorData) -> Union[ControllerDecision, None]:
        self.logger.debug('Processing request...')
        async with self.lock:
            self.logger.debug('Lock acquired.')
            self._validate_payload(data.payload)
            data.datetime = datetime.fromisoformat(data.datetime)
            # Ignore outdated data
            if data.datetime <= self.last_decision_time:
                self.logger.debug('Ignoring outdated data.')
                return
            self.latest_data.append(data.payload)

            now = get_current_time_without_microseconds()
            time_difference = now - self.last_decision_time
            self.logger.debug(
                f"Now: {now}, Last decision time: {self.last_decision_time}, Time difference: {time_difference}")

            now_str = now.isoformat()
            self.logger.debug('Checking decision time...')
            # if the time difference is less than the decision interval, return early
            if time_difference < timedelta(seconds=self.decision_interval_seconds):
                self.logger.debug('Returning early due to decision time.')
                return

            self.logger.info("Начало принятия решения.")
            last_decision_time_str = self.last_decision_time.isoformat()

            total_payload = sum(self.latest_data)
            average_payload = total_payload / len(self.latest_data)

            status = "up" if average_payload > self.status_threshold else "down"
            self.logger.info(f"Status: {status}")
            # if the status has changed, print a message, make a new decision and send it
            if status != self.previous_status:
                print(f"Status changed: {self.previous_status} -> {status}")
                decision = ControllerDecision(datetime=now, status=status)
                self.logger.info(f"Decision made: {decision}")
                await tcp_client(json.dumps(decision.model_dump(mode='json')))
            # if the last status in history is the same as the current status, update the end time
            # otherwise, add a new status to the history
            if self.history and self.history[-1].status == status:
                self.history[-1].end = now
            else:
                self.history.append(
                    Status(start=datetime.fromisoformat(last_decision_time_str), end=datetime.fromisoformat(now_str),
                           status=status))
            # update the last decision time, clear the latest data and set the previous status
            self.last_decision_time = now

            self.latest_data.clear()
            self.previous_status = status
            self.logger.debug('Finished processing request.')
            return ControllerDecision(datetime=now, status=status)

    def _format_history(self, history: List[Status]) -> List[str]:
        # Format the history list into a list of strings
        return [f"[{status.start.strftime('%H:%M:%S')} - {status.end.strftime('%H:%M:%S')} {status.status.upper()}]" for status in history]

    def _format_history_as_string(self, history: List[Status]) -> str:
        # Format the history list into a string
        formatted_history = [
            f"[{record.start.strftime('%H:%M:%S')} - {record.end.strftime('%H:%M:%S')} {record.status.upper()}]" for
            record in history]
        return ', '.join(formatted_history)

    def get_history(self) -> List[str]:
        # Get the formatted history list
        return self._format_history(self.history)

    def get_history_as_string(self) -> str:
        # Get the formatted history string
        return self._format_history_as_string(self.history)


def get_controller():
    return Controller()
