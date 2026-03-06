from langchain_core.tools import tool
import requests

@tool
def get_weather_from_coordinates(latitude: float, longitude: float):
    """
    Get the current weather conditions for a location using geographic coordinates.

    Use this tool when the user asks about:
    - Current weather at a specific place
    - Temperature at their current location
    - Weather conditions "here" or "near me"
    - Weather after obtaining latitude and longitude from another tool

    Examples:
    - "What's the weather in my location?"
    - "Current temperature here"
    - "Weather at 28.61, 77.23"

    Inputs:
        latitude (float): Geographic latitude of the location
        longitude (float): Geographic longitude of the location

    Returns:
        dict containing:
            - location (str): Name of the detected city/location
            - temperature_c (float): Current temperature in Celsius
            - condition (str): Weather condition description (e.g., Sunny, Cloudy)

    Notes:
        This tool expects valid latitude and longitude coordinates.
        Coordinates can be obtained from a location detection tool.
    """
    api="cb6b65b6dc8c47cb9bf124135230111" 
    url = "http://api.weatherapi.com/v1/current.json"

    params = {
        "key": api,
        "q": f"{latitude},{longitude}"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {
        "location": data["location"]["name"],
        "temperature_c": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"]
    }