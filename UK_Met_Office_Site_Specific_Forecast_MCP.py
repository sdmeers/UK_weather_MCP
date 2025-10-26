#!/usr/bin/env python3
import os
import logging
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastMCP server
mcp = FastMCP("UK_weather")

# Constants
MET_OFFICE_API_BASE = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point"
MET_OFFICE_API_KEY = os.getenv("MET_OFFICE_API_KEY")

if not MET_OFFICE_API_KEY:
    raise ValueError("MET_OFFICE_API_KEY environment variable not set. Please set it in your .bashrc or similar.")

# Weather code lookup table
WEATHER_CODES = {
    "NA": "Not available",
    0: "Clear night",
    1: "Sunny day",
    2: "Partly cloudy (night)",
    3: "Partly cloudy (day)",
    4: "Not used",
    5: "Mist",
    6: "Fog",
    7: "Cloudy",
    8: "Overcast",
    9: "Light rain shower (night)",
    10: "Light rain shower (day)",
    11: "Drizzle",
    12: "Light rain",
    13: "Heavy rain shower (night)",
    14: "Heavy rain shower (day)",
    15: "Heavy rain",
    16: "Sleet shower (night)",
    17: "Sleet shower (day)",
    18: "Sleet",
    19: "Hail shower (night)",
    20: "Hail shower (day)",
    21: "Hail",
    22: "Light snow shower (night)",
    23: "Light snow shower (day)",
    24: "Light snow",
    25: "Heavy snow shower (night)",
    26: "Heavy snow shower (day)",
    27: "Heavy snow",
    28: "Thunder shower (night)",
    29: "Thunder shower (day)",
    30: "Thunder"
}

def get_weather_description(code: Any) -> str:
    """Returns the human-readable description for a given weather code."""
    try:
        return WEATHER_CODES.get(int(code), f"Unknown code: {code}")
    except (ValueError, TypeError):
        return WEATHER_CODES.get(str(code), f"Unknown code: {code}")

async def _make_met_office_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
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
            logging.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None


async def _get_forecast_data(forecast_type: str, latitude: float, longitude: float) -> dict[str, Any] | None:
    """Fetches forecast data from the Met Office API."""
    url = f"{MET_OFFICE_API_BASE}/{forecast_type}"
    params = {
        "dataSource": "BD1",
        "latitude": latitude,
        "longitude": longitude,
        "includeLocationName": "true",
    }
    return await _make_met_office_request(url, params=params)


def _format_forecast_section(title: str, data: dict[str, Any]) -> str:
    """Formats a section of the forecast."""
    lines = [f"---", title]
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _parse_hourly_forecast(time_series: list[dict[str, Any]]) -> str:
    """Parses and formats the hourly forecast data."""
    forecasts = []
    for period in time_series:
        time = period.get("time", "N/A")
        temp = period.get("screenTemperature", "N/A")
        feels_like = period.get("feelsLikeTemperature", "N/A")
        humidity = period.get("screenRelativeHumidity", "N/A")
        wind_speed = period.get("windSpeed10m", "N/A")
        wind_direction = period.get("windDirectionFrom10m", "N/A")
        weather_code = period.get("significantWeatherCode", "NA")
        precipitation_rate = period.get("precipitationRate", "N/A")
        precipitation_prob = period.get("probOfPrecipitation", "N/A")
        visibility = period.get("visibility", "N/A")
        uv_index = period.get("uvIndex", "N/A")
        pressure = period.get("mslp", "N/A")

        weather_desc = get_weather_description(weather_code)

        wind_speed_mph = f"{wind_speed * 2.237:.1f}" if isinstance(wind_speed, (int, float)) else "N/A"
        pressure_mb = f"{pressure / 100:.1f}" if isinstance(pressure, (int, float)) else "N/A"
        visibility_km = f"{visibility / 1000:.1f}" if isinstance(visibility, (int, float)) else "N/A"

        forecast_data = {
            "Temperature": f'{temp}°C (feels like {feels_like}°C)',
            "Weather": weather_desc,
            "Wind": f"{wind_speed_mph} mph from {wind_direction}°",
            "Humidity": f"{humidity}%",
            "Precipitation": f"{precipitation_rate} mm/h ({precipitation_prob}% chance)",
            "Pressure": f"{pressure_mb} mb",
            "Visibility": f"{visibility_km} km",
            "UV Index": uv_index,
        }
        forecasts.append(_format_forecast_section(f"Time: {time}", forecast_data))

    return "\n".join(forecasts)


def _parse_daily_forecast(time_series: list[dict[str, Any]]) -> str:
    """Parses and formats the daily forecast data."""
    def _format(value: Any, unit: str = "", factor: float = 1.0) -> str:
        if isinstance(value, (int, float)):
            return f"{(value * factor):.1f}{unit}"
        return "N/A"

    forecasts = []
    for period in time_series:
        date = period['time'].split('T')[0]

        forecast_data = {
            "Max Temp": _format(period.get('dayMaxScreenTemperature'), "°C"),
            "Min Temp": _format(period.get('nightMinScreenTemperature'), "°C"),
            "Feels Like Max Temp": _format(period.get('dayMaxFeelsLikeTemp'), "°C"),
            "Feels Like Min Temp (Night)": _format(period.get('nightMinFeelsLikeTemp'), "°C"),
            "Day Precipitation Probability": _format(period.get('dayProbabilityOfPrecipitation'), "%"),
            "Night Precipitation Probability": _format(period.get('nightProbabilityOfPrecipitation'), "%"),
            "Max UV Index": _format(period.get('maxUvIndex')),
            "Midday Relative Humidity": _format(period.get('middayRelativeHumidity'), "%"),
            "Midday Visibility": _format(period.get('middayVisibility'), " km", 0.001),
            "Midday Pressure (MSL)": _format(period.get('middayMslp'), " hPa", 0.01),
            "Wind Speed (10m)": _format(period.get('midday10MWindSpeed'), " mph", 2.23694),
            "Weather": f"{get_weather_description(period.get('daySignificantWeatherCode', 'NA'))} (Day), "
                       f"{get_weather_description(period.get('nightSignificantWeatherCode', 'NA'))} (Night)",
        }
        forecasts.append(_format_forecast_section(f"Date: {date}", forecast_data))

    return "\n".join(forecasts)


@mcp.tool()
async def get_hourly_forecast(latitude: float, longitude: float) -> str:
    """Get the hourly weather forecast for a location in the UK."""
    data = await _get_forecast_data("hourly", latitude, longitude)
    if not data:
        return "Unable to fetch forecast data for this location."

    try:
        time_series = data["features"][0]["properties"]["timeSeries"]
        coordinates = data["features"][0]["geometry"]["coordinates"]
        location_info = f"Location: {coordinates[1]:.4f}°N, {coordinates[0]:.4f}°E"

        forecast_details = _parse_hourly_forecast(time_series)
        return f"Hourly forecast for {location_info}:\n{forecast_details}"
    except (KeyError, IndexError) as e:
        logging.error(f"Failed to parse hourly forecast data: {e}. Raw data: {data}")
        return "Failed to parse the hourly forecast data."


@mcp.tool()
async def get_daily_forecast(latitude: float, longitude: float) -> str:
    """Get the daily weather forecast for a location in the UK."""
    data = await _get_forecast_data("daily", latitude, longitude)
    if not data:
        return "Unable to fetch forecast data for this location."

    try:
        time_series = data['features'][0]['properties']['timeSeries']
        location_name = data['features'][0]['properties']['location']['name']

        forecast_details = _parse_daily_forecast(time_series)
        return f"Daily forecast for {location_name}:\n{forecast_details}"
    except (KeyError, IndexError) as e:
        logging.error(f"Failed to parse daily forecast data: {e}. Raw data: {data}")
        return "Failed to parse the daily forecast data."

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()