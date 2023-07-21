from fastapi import FastAPI

from components.controller.routers.controller import controller_router

app = FastAPI()
app.include_router(controller_router, prefix='/api/v1')

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}