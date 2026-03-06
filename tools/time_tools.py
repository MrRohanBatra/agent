from langchain_core.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo

@tool
def get_time_for_timezone(timezone: str) -> dict:
    """
    Get the current local time for a specific timezone.

    Use this tool when the user asks about the current time in a
    particular city, country, or timezone.

    Examples:
    - "What time is it in Tokyo?"
    - "Current time in London"
    - "Time in New York"
    - "Clock in Dubai"

    Input:
        timezone (str): A valid IANA timezone name.
                        Examples:
                        - "Asia/Kolkata"
                        - "America/New_York"
                        - "Europe/London"
                        - "Asia/Tokyo"

    Returns:
        dict containing:
            - timezone (str): The requested timezone
            - current_time (str): Current time in ISO 8601 format
            - formatted_time (str): Human-readable time (YYYY-MM-DD HH:MM:SS)

    Error Handling:
        Returns {"error": "Invalid timezone"} if the timezone name
        is not recognized.
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        return {
            "timezone": timezone,
            "current_time": now.isoformat(),
            "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception:
        return {"error": "Invalid timezone"}