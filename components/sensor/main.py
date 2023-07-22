import asyncio



# Сенсоры ничего не знают о состоянии других объектов, они просто отправляют свои показания и все.
from sensor.functions.sensors_functions import generate_sensor_data, SENSOR_COUNT

if __name__ == '__main__':
    print('We are sensors and we are starting!!!')
    tasks = [generate_sensor_data() for _ in range(SENSOR_COUNT)]
    asyncio.run(asyncio.wait(tasks))
