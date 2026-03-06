from langchain_core.tools import tool
import requests

@tool
def get_user_location():
    """
    Get the user's approximate geographic location based on their public IP address.

    Use this tool when the user refers to:
    - "my location"
    - "where am I"
    - "current location"
    - "near me"
    - "around me"
    - "weather here"

    This tool helps determine the user's city, country, and geographic
    coordinates which can then be used by other tools such as weather
    or nearby place searches.

    Returns:
        dict containing information such as:
            - city (str)
            - region (str)
            - country (str)
            - latitude (float)
            - longitude (float)
            - timezone (str)
            - isp (str)

    Notes:
        The location is approximate and based on the user's public IP address.
        Accuracy may vary depending on the network and ISP.
    """
    resp = requests.get("http://ip-api.com/json")
    return resp.json()