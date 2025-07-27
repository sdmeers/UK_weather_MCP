import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("UK_weather")

# Constants
MET_OFFICE_API_BASE = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point"
MET_OFFICE_API_KEY = os.getenv("MET_OFFICE_API_KEY")

if not MET_OFFICE_API_KEY:
    raise ValueError("MET_OFFICE_API_KEY environment variable not set. Please set it in your .bashrc or similar.")

async def make_met_office_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make a request to the Met Office API with proper error handling."""
    headers = {
        "accept": "application/json",
        "apikey": MET_OFFICE_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

@mcp.tool()
async def get_daily_forecast(latitude: float, longitude: float) -> str:
    """Get the daily weather forecast for a location in the UK.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
    """
    url = f"{MET_OFFICE_API_BASE}/daily"
    # The dataSource determines the forecast type. 'BD1' is for the UK 3-hourly site-specific forecast.
    # The API seems to use it for daily as well based on the endpoint.
    params = {
        "dataSource": "BD1",
        "latitude": latitude,
        "longitude": longitude,
        "includeLocationName": "true"
    }
    data = await make_met_office_request(url, params=params)

    if not data:
        return "Unable to fetch forecast data for this location."

    try:
        # According to Met Office docs, the data is nested.
        time_series = data['features'][0]['properties']['timeSeries']
        location_name = data['features'][0]['properties']['location']['name']

        forecasts = [f"Daily forecast for {location_name}:"]
        for period in time_series:
            # The time is in ISO 8601 format (e.g., "2024-05-21T12:00Z"), let's just show the date part.
            date = period['time'].split('T')[0]
            day_max_temp = period.get('dayMaxScreenTemperature', 'N/A')
            night_min_temp = period.get('nightMinScreenTemperature', 'N/A')
            day_wind_speed = period.get('midday10MWindSpeed', 'N/A')

            if day_max_temp == 'N/A' or night_min_temp == 'N/A' or day_wind_speed == 'N/A':
                print(f"Warning: Missing temperature or wind speed data for {date}. Raw data for this period: {period}")

            forecast = f"""
---
Date: {date}
Max Temp: {day_max_temp}°C
Min Temp: {night_min_temp}°C
Weather Type: {period.get('daySignificantWeatherCode', 'N/A')} (Day), {period.get('nightSignificantWeatherCode', 'N/A')} (Night)
Wind Speed (10m): {day_wind_speed} mph
"""
            forecasts.append(forecast)

        return "\n".join(forecasts)
    except (KeyError, IndexError):
        return "Failed to parse the forecast data. The structure might have changed or the location is invalid."

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')