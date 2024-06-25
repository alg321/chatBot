# weather.py

import pytz
from datetime import datetime, date
import requests
from dotenv import load_dotenv
import os
from dataclasses import dataclass


# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')

# Dataclass for WeatherData
@dataclass
class WeatherData:
    main: str
    description: str
    icon: str
    temperature: float
    humidity: float
    sunrise: str
    sunset: str
    temp_min: float
    temp_max: float
    date: str
    latitude: float
    longitude: float

# Function to convert UTC timestamp to local time
def convert_to_local_time(utc_timestamp, timezone='Europe/London'):
    """Converts UTC timestamp to local time"""
    utc_dt = datetime.utcfromtimestamp(int(utc_timestamp))
    local_tz = pytz.timezone(timezone)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime('%H:%M')

# Function to get current weather
def get_current_weather(lat, lon, api_key):
    """Fetches current weather data from OpenWeather and saves to database."""
    try:
        if api_key is None:
            raise ValueError("API_KEY is not set or is empty")

        response = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract latitude and longitude
        latitude = data.get('coord').get('lat')
        longitude = data.get('coord').get('lon')

        # Create WeatherData object
        weather_data = WeatherData(
            main=data.get('weather')[0].get('main'),
            description=data.get('weather')[0].get('description'),
            icon=data.get('weather')[0].get('icon'),
            temperature=data.get('main').get('temp'),
            humidity=data.get('main').get('humidity'),
            sunrise=convert_to_local_time(data.get('sys').get('sunrise'), 'Europe/London'),
            sunset=convert_to_local_time(data.get('sys').get('sunset'), 'Europe/London'),
            temp_min=data.get('main').get('temp_min'),
            temp_max=data.get('main').get('temp_max'),
            date=date.today().strftime('%A %dth %B'),
            latitude=latitude,  # Assign latitude and longitude to WeatherData
            longitude=longitude
        )

        return weather_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching current weather: {e}")
        return None

# Dataclass for ForecastData
@dataclass
class ForecastData:
    forecast_time: datetime
    temp_min: float
    temp_max: float
    description: str
    icon: str

# Function to get forecast weather
def get_forecast_weather(lat, lon, api_key):
    """Fetches forecast weather data from OpenWeather and saves to database."""
    try:
        response = requests.get(
            f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric'

        ).json()
        forecast_list = response.get('list', [])

        forecast_data_list = []
        for forecast in forecast_list:
            forecast_time = datetime.utcfromtimestamp(forecast['dt'])
            # Only add forecasts at noon (12:00)
            if forecast_time.hour == 12:
                forecast_data = ForecastData(
                    forecast_time=forecast_time,
                    temp_min=forecast['main']['temp_min'],
                    temp_max=forecast['main']['temp_max'],
                    description=forecast['weather'][0]['description'],
                    icon=forecast['weather'][0]['icon']
                )
                forecast_data_list.append(forecast_data)

        return forecast_data_list

    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast weather: {e}")
        return []

# Main function to fetch and store weather data
def mainFunc(selected_city=None):
    """
    Fetch and store weather data for the specified city or all cities if no city is specified.
    """
    locations = [
        ("Cumbria", "United Kingdom", 54.4609, -3.0886),
        ("Corfe Castle", "United Kingdom", 50.6395, -2.0566),
        ("The Cotswolds", "United Kingdom", 51.8330, -1.8433),
        ("Cambridge", "United Kingdom", 52.2053, 0.1218),
        ("Bristol", "United Kingdom", 51.4545, -2.5879),
        ("Oxford", "United Kingdom", 51.7520, -1.2577),
        ("Norwich", "United Kingdom", 52.6309, 1.2974),
        ("Stonehenge", "United Kingdom", 51.1789, -1.8262),
        ("Watergate Bay", "United Kingdom", 50.4429, -5.0553),
        ("Birmingham", "United Kingdom", 52.4862, -1.8904)
    ]

    from app import db  # Importing 'db' locally in mainFunc to prevent circular error

    weather_data_list = []

    for name, country, lat, lon in locations:
        if selected_city and selected_city.lower().replace(" ", "_") != name.lower().replace(" ", "_"):
            continue  # Skip if a specific city is selected and it doesn't match the current city

        # Fetch current weather data
        current_weather_data = get_current_weather(lat, lon, api_key)
        if current_weather_data:
            # Fetch forecast weather data
            forecast_weather_data = get_forecast_weather(lat, lon, api_key)

            # Create and save CurrentWeather instance to database
            from models.models import CurrentWeather  # Import here to avoid circular import

            current_weather = CurrentWeather(
                city=name,
                country=country,
                main=current_weather_data.main,
                description=current_weather_data.description,
                icon=current_weather_data.icon,
                temperature=current_weather_data.temperature,
                humidity=current_weather_data.humidity,
                sunrise=current_weather_data.sunrise,
                sunset=current_weather_data.sunset,
                temp_min=current_weather_data.temp_min,
                temp_max=current_weather_data.temp_max,
            )
            db.session.add(current_weather)

            # Create and save ForecastWeather instances to database
            from models.models import ForecastWeather  # Import here to avoid circular import

            for forecast_data in forecast_weather_data:
                forecast_weather = ForecastWeather(
                    city=name,
                    country=country,
                    forecast_time=forecast_data.forecast_time,
                    temp_min=forecast_data.temp_min,
                    temp_max=forecast_data.temp_max,
                    description=forecast_data.description,
                    icon=forecast_data.icon,
                    current_weather=current_weather  # Establish relationship
                )
                db.session.add(forecast_weather)

            # Commit all changes to the database
            db.session.commit()

            # Append to weather_data_list
            weather_data_list.append((name, country, current_weather_data, forecast_weather_data))

    return weather_data_list

