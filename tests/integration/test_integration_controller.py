# import asyncio
# import logging
# import os
# from unittest.mock import patch
#
# import pytest
# from asynctest import Mock
# from fastapi.testclient import TestClient
#
# from components.controller.main import send_start_message, app
# from components.sensor.main import wait_for_start_message
# from components.controller.functions.controller_functions import Controller
#
# # Create a logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
#
# # Create a file handler
# handler = logging.FileHandler('test_log.log')
#
# # Set the level of the handler. This can be DEBUG, INFO, ERROR, etc.
# handler.setLevel(logging.DEBUG)
#
# # Create a formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
# # Add the formatter to the handler
# handler.setFormatter(formatter)
#
# # Add the handler to the logger
# logger.addHandler(handler)
#
#
# class SensorManager:
#     def __init__(self, start_event):
#         self.start_event = start_event
#         self.task = asyncio.wait_for(self._run_sensor(), 20)
#
#     async def _run_sensor(self):
#         await self.start_event.wait()
#         while True:
#             logger.info("Sensor is running")
#             wait_for_start_message()
#
#     def stop(self):
#         self.task.cancel()
#
#
# class ControllerManager:
#     def __init__(self, start_event):
#         self.start_event = start_event
#         self.task = asyncio.wait_for(self._run_controller(), 20)
#
#     async def _run_controller(self):
#         logger.info("Controller is running")
#         send_start_message()
#         self.start_event.set()
#
#     def stop(self):
#         self.task.cancel()
#
#
# @pytest.fixture(autouse=True)
# def reset_controller():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     controller = Controller()
#     controller.reset()
#     return controller
#
#
# def test_get_history(reset_controller):
#     # Arrange
#     reset_controller.get_history = Mock(return_value=["[12:00:00 - 12:00:05 UP]"])
#     with patch('components.controller.functions.controller_functions.get_controller', return_value=reset_controller):
#         client = TestClient(app)
#
#         # Act
#         response = client.get("/api/v1/controller/history")
#
#         # Assert
#         assert response.status_code == 200
#         assert response.json() == ["[12:00:00 - 12:00:05 UP]"]
#
#
# def test_get_history_string(reset_controller):
#     # Arrange
#     mock_controller = Mock(spec=Controller)
#     mock_controller.get_history_as_string.return_value = "12:00:00 - 12:00:05 UP, 12:00:06 - 12:00:11 DOWN"
#
#     reset_controller.get_history_as_string = mock_controller.get_history_as_string
#
#     client = TestClient(app)
#
#     # Act
#     response = client.get("/api/v1/controller/history_string")
#
#     # Assert
#     assert response.status_code == 200
#     assert response.json() == "12:00:00 - 12:00:05 UP, 12:00:06 - 12:00:11 DOWN"

# @pytest.mark.asyncio
# async def test_sensor_endpoint(reset_controller):
#     start_event = asyncio.Event()
#     # controller_manager = ControllerManager(start_event)
#     sensor_manager = SensorManager(start_event)
#
#     print('Loop starts')
#     for _ in range(3000):
#         if reset_controller.previous_status is not None:
#             break
#         await asyncio.sleep(0.001)  # Yield control to other tasks
#     print('Loop ends')
#
#     # Stop the controller and sensor
#     # controller_manager.stop()
#     sensor_manager.stop()

# Assert
# assert reset_controller.previous_status in {'up', 'down'}
