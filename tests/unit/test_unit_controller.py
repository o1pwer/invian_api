import asyncio
import time
from datetime import timedelta
from unittest.mock import patch

import pytest

from components.controller.functions.controller_functions import Controller, get_current_time_without_microseconds
from components.controller.schemas.response import ControllerDecision
from invian_shared.shared_exceptions import BadPayloadException
from invian_shared.shared_schemas import SensorData


@pytest.fixture(autouse=True)
def reset_controller():
    controller = Controller()
    controller.reset()
    return controller


# Test if the controller correctly determines the status as "up" when the average is above the threshold
@pytest.mark.asyncio
@patch('components.controller.functions.controller_functions.tcp_client')
async def test_status_up(mock_tcp_client, reset_controller):
    mock_tcp_client.return_value = None
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
        decision = await reset_controller.process_request(data)
        await asyncio.sleep(0.001)

    # Check that the decision status is "up"
    assert decision.status == "up"


# Test for "down" status
@pytest.mark.asyncio
@patch('components.controller.functions.controller_functions.tcp_client')
async def test_status_down(mock_tcp_client, reset_controller):
    mock_tcp_client.return_value = None
    decision = None

    time_limit = 20
    start_time = time.time()

    while decision is None:
        if time.time() - start_time > time_limit:
            raise Exception("Test took too much time")

        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=40)
        decision = await reset_controller.process_request(data)
        await asyncio.sleep(0.001)

    assert decision.status == "down"


# Test for very large payload values
@pytest.mark.asyncio
@patch('components.controller.functions.controller_functions.tcp_client')
async def test_status_corner_case_up(mock_tcp_client, reset_controller):
    mock_tcp_client.return_value = None
    for _ in range(300):
        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=99999999999999999999)
        with pytest.raises(BadPayloadException):
            await reset_controller.process_request(data)
        await asyncio.sleep(0.001)


# Test for very small payload values
# Test for very large payload values
@pytest.mark.asyncio
@patch('components.controller.functions.controller_functions.tcp_client')
async def test_status_corner_case_down(mock_tcp_client, reset_controller):
    mock_tcp_client.return_value = None
    for _ in range(300):
        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=-99999999999999999999)
        with pytest.raises(BadPayloadException):
            await reset_controller.process_request(data)
        await asyncio.sleep(0.001)

# Test if the controller correctly sets the time in the decision
@pytest.mark.asyncio
@patch('components.controller.functions.controller_functions.tcp_client')
async def test_datetime(mock_tcp_client, reset_controller):
    mock_tcp_client.return_value = None
    decision = None

    time_limit = 20
    start_time = time.time()

    while decision is None:
        if time.time() - start_time > time_limit:
            raise Exception("Test took too much time")

        data = SensorData(datetime=get_current_time_without_microseconds().isoformat(), payload=40)
        decision = await reset_controller.process_request(data)
        await asyncio.sleep(0.001)

    # Check that the time in the controller's decision matches the current time (ignoring seconds)
    if not isinstance(decision, ControllerDecision):
        pytest.fail(f"Expected decision to be a ControllerDecision instance but got {type(decision)} instead")
    assert decision.datetime.replace(second=0) == get_current_time_without_microseconds().replace(second=0)


# Test if the controller correctly ignores outdated data
@pytest.mark.asyncio
@patch('components.controller.functions.controller_functions.tcp_client')
async def test_ignore_outdated_data(mock_tcp_client, reset_controller):
    mock_tcp_client.return_value = None
    # Generate sensor data with an outdated timestamp
    outdated_data = SensorData(datetime=(get_current_time_without_microseconds() - timedelta(seconds=10)).isoformat(), payload=60)
    # The controller should ignore this data and not make a decision
    decision = await reset_controller.process_request(outdated_data)
    assert decision is None
