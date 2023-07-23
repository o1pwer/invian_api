import asyncio
import time
from datetime import timedelta

import pytest

from controller.exceptions.controller_exceptions import BadPayloadException
from controller.functions.controller_functions import Controller, get_current_time_without_microseconds
from controller.schemas.request import SensorData


# Fixture to create a controller before each test
@pytest.fixture
def controller():
    return Controller(status_threshold=50)


# Test if the controller correctly determines the status as "up" when the average is above the threshold
@pytest.mark.asyncio
async def test_status_up(controller):
    # Initialize the decision as None
    decision = None

    # Set a time limit for the test
    time_limit = 20
    start_time = time.time()

    # Wait until the controller makes a decision
    while decision is None:
        # Raise an exception if the test takes too much time
        if time.time() - start_time > time_limit:
            raise Exception("Test took too much time")

        # Generate sensor data
        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=60)
        # Ask the controller to process the data
        decision = await controller.process_request(data)
        await asyncio.sleep(0.001)

    # Check that the decision status is "up"
    assert decision.status == "up"


# Test for "down" status
@pytest.mark.asyncio
async def test_status_down(controller):
    decision = None

    time_limit = 20
    start_time = time.time()

    while decision is None:
        if time.time() - start_time > time_limit:
            raise Exception("Test took too much time")

        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=40)
        decision = await controller.process_request(data)
        await asyncio.sleep(0.001)

    assert decision.status == "down"


# Test for very large payload values
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


# Test if the controller correctly sets the time in the decision
@pytest.mark.asyncio
async def test_datetime(controller):
    decision = None

    time_limit = 20
    start_time = time.time()

    while decision is None:
        if time.time() - start_time > time_limit:
            raise Exception("Test took too much time")

        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=40)
        decision = await controller.process_request(data)
        await asyncio.sleep(0.001)

    # Check that the time in the controller's decision matches the current time (ignoring seconds)
    assert decision.datetime.replace(second=0) == get_current_time_without_microseconds().replace(second=0)


# Test if the controller correctly ignores outdated data
@pytest.mark.asyncio
async def test_ignore_outdated_data(controller):
    # Generate sensor data with an outdated timestamp
    outdated_data = SensorData(datetime=(get_current_time_without_microseconds() - timedelta(seconds=10)).isoformat(), payload=60)
    # The controller should ignore this data and not make a decision
    decision = await controller.process_request(outdated_data)
    assert decision is None
