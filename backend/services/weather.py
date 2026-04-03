import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = "Mumbai") -> dict:
    if not WEATHER_API_KEY or WEATHER_API_KEY == "your_openweather_api_key_here":
        return {
            "city": city,
            "temperature": 28.5,
            "description": "partly cloudy (mock)",
            "humidity": 72,
            "demand_signal": "normal",
        }
    try:
        resp = requests.get(
            BASE_URL,
            params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"},
            timeout=5,
        )
        data = resp.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        signal = "high" if temp > 35 or "rain" in desc else "normal"
        return {"city": city, "temperature": temp, "description": desc, "humidity": humidity, "demand_signal": signal}
    except Exception as e:
        return {"city": city, "error": str(e), "demand_signal": "unknown"}
