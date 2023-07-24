import asyncio
import logging
import time
import traceback

import pika

from functions.sensors_functions import Sensor

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def callback(ch, method, properties, body):
    logger.debug(" [x] Received %r" % body)
    sensor = Sensor(logger=logger)
    logging.info('We are sensors and we are starting!!!')
    tasks = [sensor.generate_sensor_data() for _ in range(sensor.sensor_count)]
    asyncio.run(asyncio.wait(tasks))


def wait_for_start_message():
    backoff = 1
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()

            channel.queue_declare(queue='start_queue')

            logger.debug(' [*] Waiting for start messages. To exit press CTRL+C')

            channel.basic_consume(queue='start_queue', on_message_callback=callback, auto_ack=True)

            channel.start_consuming()
            break  # If we've gotten this far, the connection was successful, so we can exit the loop.
        except pika.exceptions.AMQPConnectionError as exc:
            logger.warning(f"RabbitMQ is not up yet!\nWaiting for {backoff} seconds, then reconnecting...")
            time.sleep(backoff)
            backoff *= 2  # Double the backoff time for the next iteration.
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    while True:
        wait_for_start_message()
