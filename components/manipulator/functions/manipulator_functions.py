import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

from aiohttp import web


class MockServer:
    def __init__(self):
        self.start = AsyncMock()
        self.cleanup = AsyncMock()


class Manipulator:
    """
        This class represents a Manipulator which receives status updates from a Controller via HTTP requests.

        The Manipulator runs an aiohttp server and listens for incoming requests on a specified endpoint.
        When a request is received, it validates the status and updates its current status accordingly.

        Attributes:
            VALID_STATUSES (tuple): Valid statuses that can be received.
            SERVER_ADDRESS (str): Address where the server is running.
            SERVER_PORT (int): Port where the server is listening.
            ENDPOINT (str): Endpoint where the server receives status updates.
            current_status (str): Current status of the manipulator.
            server (web.AppRunner): The aiohttp server.
            stop_event (asyncio.Event): Event to signal the server to stop.
            server_run_event (asyncio.Event): Event to signal when the server is running.
            logger (logging.Logger): A logger instance for logging information.

        Methods:
            handle_request(request: web.Request) -> web.Response:
                Handle incoming requests, validate the status, and update the current_status.
            get_status() -> str:
                Return the current status.
            run_server() -> None:
                Run the aiohttp server.
            stop_server() -> None:
                Stop the aiohttp server.
        """
    VALID_STATUSES = ('up', 'down')
    SERVER_PORT = 8080
    ENDPOINT = '/'
    SERVER_ADDRESS = 'manipulator'

    def __init__(self, server=None, mock=False):
        self.current_status = ""
        self.server = server
        self.mock = mock
        self.stop_event = asyncio.Event()
        self.server_run_event = asyncio.Event()
        self.logger = logging.getLogger()

    async def handle_request(self, request):
        """Handle incoming requests, validate the status, and update the current_status."""
        try:
            data = await request.json()
        except Exception as e:
            self.logger.error(f"Error parsing request: {e}")
            return web.json_response({"error": "Error parsing request."}, status=400)

        received_status = data.get('status')
        if not received_status:
            self.logger.warning("Didn't receive any status. Ignoring.")
            return web.json_response({"error": "No status received."}, status=400)

        if received_status not in self.VALID_STATUSES:
            self.logger.warning(f"Received unusual status: {received_status}. Ignoring.")
            return web.json_response(
                {"error": f"Invalid status received: {received_status}. Expected one of {self.VALID_STATUSES}."},
                status=400)

        self.current_status = received_status
        self.logger.info(f"Received data: {data}")
        return web.Response()

    def get_status(self):
        """Return the current status."""
        return self.current_status

    async def run_server(self):
        """Run the aiohttp server."""
        self.logger.info("Running server...")
        if self.mock:
            await self.mock_run_server()
        else:
            await self.real_run_server()
        self.logger.info("Server is running.")

    async def mock_run_server(self):
        """Run as a mock server."""
        app = web.Application()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner)
        await site.start()
        self.server = runner
        self.server_run_event.set()

        await self.server_run_event.wait()
        self.logger.info("Mock server is stopping.")

    async def real_run_server(self):
        """Run as a real server."""
        app = web.Application()
        app.add_routes([web.post(self.ENDPOINT, self.handle_request)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.SERVER_ADDRESS, self.SERVER_PORT)
        await site.start()

        self.server = runner
        await self.server_run_event.wait()


async def stop_server(self):
        """Stop the aiohttp server."""
        self.logger.info("Stopping server...")
        self.server_run_event.clear()
        if self.server is not None:
            await self.server.cleanup()
            self.server = None
        self.logger.info("Server stopped.")
