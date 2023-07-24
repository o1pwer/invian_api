import logging

import httpx

logger = logging.getLogger()

async def tcp_client(message: str, server_address='manipulator', server_port=8080):
    url = f"http://{server_address}:{server_port}/"
    logger.debug(f"Connecting to {url}")
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, data=message)
        except httpx.ConnectError:
            logger.warning("Failed to connect to the server.")
            return
        logger.debug(f"Sending {message}")
        logger.debug("Closing socket")
