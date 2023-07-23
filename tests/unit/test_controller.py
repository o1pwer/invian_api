import asyncio
import time

import pytest

from controller.exceptions.controller_exceptions import BadPayloadException
from controller.functions.controller_functions import Controller, get_current_time_without_microseconds
from controller.schemas.request import SensorData


# Фикстура для создания контроллера перед каждым тестом
@pytest.fixture
def controller():
    return Controller(status_threshold=50)


# Проверяем, что контроллер правильно определяет статус как "up", когда среднее значение больше порогового
@pytest.mark.asyncio
async def test_status_up(controller):
    # Инициализируем решение как None
    decision = None

    # Определяем временной лимит для теста
    time_limit = 20
    start_time = time.time()

    # Ждем, пока контроллер не примет решение
    while decision is None:
        # Если тест занимает слишком много времени, выбрасываем исключение
        if time.time() - start_time > time_limit:
            raise Exception("Тест занял слишком много времени")

        # Генерируем данные от сенсора
        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=60)
        # Просим контроллер обработать данные
        decision = await controller.process_request(data)
        await asyncio.sleep(0.001)

    # Проверяем, что статус решения - "up"
    assert decision.status == "up"


# Тест на проверку статуса "down"
@pytest.mark.asyncio
async def test_status_down(controller):
    decision = None

    time_limit = 20
    start_time = time.time()

    while decision is None:
        if time.time() - start_time > time_limit:
            raise Exception("Тест занял слишком много времени")

        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=40)
        decision = await controller.process_request(data)
        await asyncio.sleep(0.001)

    assert decision.status == "down"


@pytest.mark.asyncio
async def test_status_corner_case_up(controller):
    for _ in range(300):
        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=99999999999999999999)
        with pytest.raises(BadPayloadException):
            await controller.process_request(data)
        await asyncio.sleep(0.001)


# Test for very small payload values
@pytest.mark.asyncio
async def test_status_corner_case_down(controller):
    for _ in range(300):
        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=-99999999999999999999)
        with pytest.raises(BadPayloadException):
            await controller.process_request(data)
        await asyncio.sleep(0.001)


# Проверяем, что контроллер правильно устанавливает время в решении
@pytest.mark.asyncio
async def test_datetime(controller):
    decision = None

    time_limit = 20
    start_time = time.time()

    while decision is None:
        if time.time() - start_time > time_limit:
            raise Exception("Тест занял слишком много времени")

        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=40)
        decision = await controller.process_request(data)
        await asyncio.sleep(0.001)

    # Проверяем, что время в решении контроллера совпадает с текущим временем (без учета секунд)
    assert decision.datetime.replace(second=0) == get_current_time_without_microseconds().replace(second=0)
