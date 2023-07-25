from unittest.mock import AsyncMock

import pytest

from components.manipulator.functions.manipulator_functions import Manipulator


@pytest.mark.asyncio
async def test_manipulator_handle_request():
    # Arrange
    manipulator = Manipulator()
    request = AsyncMock()
    request.json.return_value = {"status": "up"}

    # Act
    response = await manipulator.handle_request(request)

    # Assert
    assert manipulator.get_status() == "up"
    assert response.status == 200


@pytest.mark.asyncio
async def test_manipulator_handle_invalid_request():
    # Arrange
    manipulator = Manipulator()
    request = AsyncMock()
    request.json.return_value = {"status": "invalid_status"}

    # Act
    response = await manipulator.handle_request(request)

    # Assert
    assert manipulator.get_status() == ""
    assert response.status == 400
