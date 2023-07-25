from unittest.mock import AsyncMock

import pytest

from components.manipulator.functions.manipulator_functions import Manipulator


@pytest.mark.asyncio
async def test_manipulator_handle_request():
    manipulator = Manipulator()
    request = AsyncMock()
    request.json.return_value = {"status": "up"}

    response = await manipulator.handle_request(request)

    assert manipulator.get_status() == "up"
    assert response.status == 200


@pytest.mark.asyncio
async def test_manipulator_handle_invalid_request():
    manipulator = Manipulator()
    request = AsyncMock()
    request.json.return_value = {"status": "invalid_status"}

    response = await manipulator.handle_request(request)

    assert manipulator.get_status() == ""
    assert response.status == 400


@pytest.mark.asyncio
async def test_manipulator_handle_request_no_status():
    manipulator = Manipulator()
    request = AsyncMock()
    request.json.return_value = {}

    response = await manipulator.handle_request(request)

    assert manipulator.get_status() == ""
    assert response.status == 400