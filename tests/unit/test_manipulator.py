import asyncio

import httpx
import pytest

from manipulator.functions.manipulator_functions import Manipulator


@pytest.mark.asyncio
async def test_manipulator():
    # Creating Manipulator and server in separate task
    manipulator = Manipulator()
    server_task = asyncio.create_task(manipulator.run_server())

    # Waiting for server to start
    await asyncio.sleep(0.1)

    # Sending new status to manipulator
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'status': 'up'})

    # Waiting for manipulator to process what we've sent to it
    await asyncio.sleep(0.1)

    # Checking if the status has actually updated.
    assert manipulator.get_status() == 'up'

    # Same with other status.
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'status': 'down'})

    await asyncio.sleep(0.1)

    assert manipulator.get_status() == 'down'
    # Stopping the server.
    await manipulator.stop_server()
    await server_task


@pytest.mark.asyncio
async def test_manipulator_corner_cases():
    manipulator = Manipulator()
    server_task = asyncio.create_task(manipulator.run_server())

    await asyncio.sleep(0.1)
    # Sending wrong status
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'status': 'hbgjkmuy,'})

    await asyncio.sleep(0.1)

    # Checking that status doesn't change
    assert manipulator.get_status() == ''

    # Sending a completely wrong data
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'foo': 'bar'})

    await asyncio.sleep(0.1)

    assert manipulator.get_status() == ''
    await manipulator.stop_server()
    await server_task
