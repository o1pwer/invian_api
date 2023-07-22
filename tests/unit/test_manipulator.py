import httpx
import asyncio

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



