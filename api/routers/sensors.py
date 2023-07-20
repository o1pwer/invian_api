from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

@router.get("/sensor/read")
async def read_sensor():
    """Reads a sensor reading."""
    reading = await sensor()
    return reading