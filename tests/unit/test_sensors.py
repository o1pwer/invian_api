import logging
import time
from unittest.mock import patch, MagicMock, Mock

import httpx
import pytest
from httpx import Response

from components.sensor.functions.sensors_functions import generate_sensor_data

logger = logging.getLogger(__name__)
# Накидай тут угарных комментов.
def count_calls(num_calls: list):
    # Функция, которая просто подсчитывает, сколько раз ее вызвали.
    def side_effect(*args, **kwargs):
        num_calls[0] += 1
        return Response(200)

    return side_effect



@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_generate_sensor_data(mock_client):
    iterations = 5
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    await generate_sensor_data(iterations)
    assert mock_client.return_value.__aenter__.return_value.post.call_count == iterations

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_payload_range(mock_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    iterations = 5
    await generate_sensor_data(iterations)
    for call in mock_client.return_value.__aenter__.return_value.post.call_args_list:
        payload = call.kwargs['json']['payload']
        assert 0 <= payload <= 100

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_payload_type(mock_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    iterations = 5
    await generate_sensor_data(iterations)
    for call in mock_client.return_value.__aenter__.return_value.post.call_args_list:
        response = call.kwargs['json']
        assert isinstance(response.get('payload'), int)
        assert isinstance(response.get('datetime'), str)

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_connection_error_handling(mock_client):
    iterations = 5
    mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.ConnectError('Error', request=Mock())
    start_time = time.time()
    await generate_sensor_data(iterations)
    end_time = time.time()
    assert end_time - start_time >= 5
    assert mock_client.return_value.__aenter__.return_value.post.call_count == iterations

