from fastapi import APIRouter, Query
from services.weather import get_weather

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/")
def weather(city: str = Query("Mumbai")):
    return get_weather(city)
