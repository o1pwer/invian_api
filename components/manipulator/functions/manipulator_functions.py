import asyncio
import json
from aiohttp import web

class Manipulator:
    def __init__(self):
        self.current_status = ""
        self.server = None
        self.stop_event = asyncio.Event()
        self.server_run_event = asyncio.Event()

    async def handle_request(self, request):
        data = await request.json()
        self.current_status = data.get('status')
        print(f"Received data: {data}")
        return web.Response()

    def get_status(self):
        return self.current_status

    async def run_server(self):
        app = web.Application()
        app.add_routes([web.post('/', self.handle_request)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()

        self.server = runner

        # Тут мы ждем, пока нам прикажут остановиться. Мы - это типа сервер =)
        await self.server_run_event.wait()

    async def stop_server(self):
        # Грубо говоря, мы приказываем серверу остановиться.
        self.server_run_event.set()

        # Ждем, пока он остановится.
        await self.server.cleanup()