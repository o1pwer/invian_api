import asyncio

import httpx
import pytest

from manipulator.functions.manipulator_functions import Manipulator


@pytest.mark.asyncio
async def test_manipulator():
    # Создадим манипулятор и сервак в отдельной таске
    manipulator = Manipulator()
    server_task = asyncio.create_task(manipulator.run_server())

    # Ждем, пока сервак запустится. (можно сделать и умнее)
    await asyncio.sleep(0.1)

    # Отправим новый статус манипулятору.
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'status': 'up'})

    # Ждем обработку запроса серверов (да, я знаю, я немножко ленивый)
    await asyncio.sleep(0.1)

    # Проверяем, как обновился статус манипулятора.
    assert manipulator.get_status() == 'up'

    # Соответственно, делаем то же самое, только с другим статусом.
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'status': 'down'})

    await asyncio.sleep(0.1)

    assert manipulator.get_status() == 'down'
    # Сервер можно остановить
    await manipulator.stop_server()
    await server_task


@pytest.mark.asyncio
async def test_manipulator_corner_cases():
    manipulator = Manipulator()
    server_task = asyncio.create_task(manipulator.run_server())

    await asyncio.sleep(0.1)
    # Отправляем непонятно что вместо статуса.
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'status': 'hbgjkmuy,'})

    await asyncio.sleep(0.1)

    # Проверяем, что статус манипулятора не изменился и все так же пуст.
    assert manipulator.get_status() == ''

    # Соответственно, делаем то же самое, только с полным отсутствием статуса в запросе.
    async with httpx.AsyncClient() as client:
        await client.post('http://localhost:8080/', json={'foo': 'bar'})

    await asyncio.sleep(0.1)

    assert manipulator.get_status() == ''
    await manipulator.stop_server()
    await server_task
