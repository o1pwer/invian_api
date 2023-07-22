import asyncio

from manipulator.functions.manipulator_functions import Manipulator

if __name__ == "__main__":
    async def main():
        manipulator = Manipulator()
        await manipulator.run_server()

        try:
            while True:
                # Wait for a second at a time until interrupted
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            await manipulator.stop_server()

    asyncio.run(main())