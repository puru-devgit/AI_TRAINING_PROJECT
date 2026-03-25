import requests

API_KEY = "b3eae4351f337912a4b9882a91835ade"


# Day 1 → Fetch weather data
def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"

    response = requests.get(url)
    data = response.json()

    weather = data["weather"][0]["main"]
    temp = data["main"]["temp"]

    return weather, temp


# Day 2 → Risk detection
def check_risk(city):

    weather, temp = get_weather(city)

    if weather == "Rain":
        return "Delivery delay possible"

    elif weather == "Thunderstorm":
        return "High supply chain risk"

    else:
        return "No major risk"


# Run the program
city = "Bhubaneswar"

weather, temp = get_weather(city)
risk = check_risk(city)

print("City:", city)
print("Weather:", weather)
print("Temperature:", temp)
print("Risk Alert:", risk)