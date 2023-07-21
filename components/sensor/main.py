import asyncio

from components.sensor.functions.sensors import run_sensor_tasks, generate_sensor_data, SENSOR_COUNT

# Сенсоры ничего не знают о состоянии других объектов, они просто отправляют свои показания и все.
if __name__ == '__main__':
    tasks = [generate_sensor_data(i) for i in range(SENSOR_COUNT)]
    asyncio.run(asyncio.wait(tasks))
