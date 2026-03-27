import requests

API_KEY = "b3eae4351f337912a4b9882a91835ade"

risk_data = {
    "Rain": "Heavy rain can delay transportation and delivery of goods.",
    "Thunderstorm": "Thunderstorms may disrupt logistics and supply routes.",
    "Clouds": "Minimal impact on transportation.",
    "Clear": "No major supply chain risk."
}

# Day 1
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data["weather"][0]["main"]

# Day 3
def retrieve_risk(weather):
    if weather in risk_data:
        return risk_data[weather]
    else:
        return "No risk information available"

#  Day 4
def supply_decision(risk):

    if "delay" in risk.lower():
        return "Reorder inventory earlier"

    elif "disrupt" in risk.lower():
        return "Increase safety stock"

    else:
        return "Normal supply chain operation"


city = "Bhubaneswar"

weather = get_weather(city)
risk = retrieve_risk(weather)
decision = supply_decision(risk)

print("Weather:", weather)
print("Risk:", risk)
print("Decision:", decision)