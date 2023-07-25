import asyncio
import logging

from functions.manipulator_functions import Manipulator
logger = logging.getLogger()

async def main():
    manipulator = Manipulator()
    try:
        await manipulator.run_server()
        logger.warning('Bip!')
        while True:
            # Wait for a second at a time until interrupted
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logger.warning(f"Error: {exc}")
    finally:
        await manipulator.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
