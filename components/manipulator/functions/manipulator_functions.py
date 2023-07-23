import asyncio
import logging

from aiohttp import web


class Manipulator:
    VALID_STATUSES = ('up', 'down')
    SERVER_ADDRESS = 'localhost'
    SERVER_PORT = 8080
    ENDPOINT = '/'

    def __init__(self):
        self.current_status = ""
        self.server = None
        self.stop_event = asyncio.Event()
        self.server_run_event = asyncio.Event()
        self.logger = logging.getLogger()

    async def handle_request(self, request):
        """Handle incoming requests, validate the status, and update the current_status."""
        data = await request.json()
        received_status = data.get('status')
        if not received_status:
            self.logger.warning("Didn't recieve any status. Ignoring.")
            return web.json_response({"error": "No status received."}, status=400)
        if received_status not in self.VALID_STATUSES:
            self.logger.warning(f"Recieved unusual status: {received_status}. Ignoring.")
            return web.json_response({"error": f"Invalid status received: {received_status}."
                                               f" Expected one of {self.VALID_STATUSES}."}, status=400)
        self.current_status = data.get('status')
        print(f"Received data: {data}")
        return web.Response()

    def get_status(self):
        """Return the current status."""
        return self.current_status

    async def run_server(self):
        """Run the aiohttp server."""
        app = web.Application()
        app.add_routes([web.post(self.ENDPOINT, self.handle_request)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.SERVER_ADDRESS, self.SERVER_PORT)
        await site.start()

        self.server = runner

        # Wait for the stop signal.
        await self.server_run_event.wait()

    async def stop_server(self):
        """Stop the aiohttp server."""
        # Trigger the stop signal.
        self.server_run_event.set()

        # Wait for the server to stop.
        await self.server.cleanup()
