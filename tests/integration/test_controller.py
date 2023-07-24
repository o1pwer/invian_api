import time
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from components.controller.functions.controller_functions import Controller
from components.controller.main import app


@pytest.fixture(autouse=True)
def reset_controller():
    controller = Controller()
    controller.reset()


def test_get_history():
    # Arrange
    mock_controller = Mock(spec=Controller)
    mock_controller.get_history.return_value = ["[12:00:00 - 12:00:05 UP]"]

    controller = Controller()
    controller.get_history = mock_controller.get_history

    client = TestClient(app)

    # Act
    response = client.get("/api/v1/controller/history")

    # Assert
    assert response.status_code == 200
    assert response.json() == ["[12:00:00 - 12:00:05 UP]"]


def test_get_history_string():
    # Arrange
    mock_controller = Mock(spec=Controller)
    mock_controller.get_history_as_string.return_value = "12:00:00 - 12:00:05 UP, 12:00:06 - 12:00:11 DOWN"

    controller = Controller()
    controller.get_history_as_string = mock_controller.get_history_as_string

    client = TestClient(app)

    # Act
    response = client.get("/api/v1/controller/history_string")

    # Assert
    assert response.status_code == 200
    assert response.json() == "12:00:00 - 12:00:05 UP, 12:00:06 - 12:00:11 DOWN"


def test_sensor_endpoint():
    # Arrange
    controller = Controller()
    controller.reset()

    sensor_data = {
        "datetime": "2023-07-20T12:00:00",
        "payload": 60,
    }

    client = TestClient(app)

    # Act
    response = None
    for _ in range(3000):
        response = client.post("/api/v1/controller/send_request", json=sensor_data)
        time.sleep(0.001)
        # If the controller has made a decision, stop the loop
        if response.json() is not None:
            break

    # Assert
    assert response.status_code == 200
    assert response.json().get('status') == 'up'
