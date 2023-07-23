from unittest.mock import AsyncMock

import httpx
import pytest

from sensor.functions.sensors_functions import Sensor


@pytest.mark.asyncio
async def test_sensor_generate_sensor_data(mocker):
    # Arrange
    sensor = Sensor(messages_per_second=1)
    mocker.patch.object(httpx.AsyncClient, "post", return_value=AsyncMock())

    # Act
    await sensor.generate_sensor_data(iterations=1)

    # Assert
    httpx.AsyncClient.post.assert_called_once()


@pytest.mark.asyncio
async def test_sensor_generate_sensor_data_with_connect_error(mocker):
    # Arrange
    sensor = Sensor(messages_per_second=1)
    mocker.patch.object(httpx.AsyncClient, "post", side_effect=Exception)

    # Act
    with pytest.raises(Exception):
        await sensor.generate_sensor_data(iterations=1)

    # Assert
    assert httpx.AsyncClient.post.call_count == 1
