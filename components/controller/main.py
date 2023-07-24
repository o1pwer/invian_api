import logging
import time
import traceback

import pika
import uvicorn
from fastapi import FastAPI

from components.controller.functions.controller_functions import Controller
from components.controller.routers.controller_router import controller_router

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, handlers=[logging.StreamHandler()])
logger = logging.getLogger()
app = FastAPI(logging=True)


def send_start_message():
    backoff = 1
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()

            channel.queue_declare(queue='start_queue')

            channel.basic_publish(exchange='',
                                  routing_key='start_queue',
                                  body='start')
            logger.debug(" [x] Sent 'start'")
            connection.close()
            break
        except pika.exceptions.AMQPConnectionError as exc:
            logger.warning(f"RabbitMQ is not up yet!\nWaiting for {backoff} seconds, then reconnecting...")
            time.sleep(backoff)
            backoff *= 2
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(traceback.format_exc())


@app.on_event("startup")
async def startup_event():
    app.state.controller = Controller(status_threshold=50)
    send_start_message()


app.include_router(controller_router, prefix='/api/v1')

uvicorn.run(app=app, host='controller', port=8000)
