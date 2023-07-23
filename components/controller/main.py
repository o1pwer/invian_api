import logging

from fastapi import FastAPI

from controller.functions.controller_functions import Controller
from controller.routers.controller_router import controller_router

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, handlers=[logging.StreamHandler()])
app = FastAPI(logging=False)


@app.on_event("startup")
async def startup_event():
    app.state.controller = Controller(status_threshold=50)


app.include_router(controller_router, prefix='/api/v1')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
