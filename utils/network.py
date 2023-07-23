import httpx


async def tcp_client(message: str, server_address='localhost', server_port=8080):
    url = f"http://{server_address}:{server_port}/"
    print(f"Подключаемся к {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=message)
        except httpx.ConnectError:
            print("Не удалось подключиться к серверу")
            return
        print(f"Отправляем {message}")
        print("Закрываем сокет")
