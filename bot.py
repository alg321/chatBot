import logging
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from chatterbot.conversation import Statement
import spacy
from datetime import datetime, timedelta, time
from sqlalchemy import desc
from app import app  # Import app from your Flask application
from models.models import CurrentWeather, ForecastWeather
import dateparser

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Create chatbot instance
chatbot = ChatBot("WeatherBot")

# Train the bot with the corpus data
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")

# Train the bot with custom weather-related conversations
from weather_conversations import weather_conversations

list_trainer = ListTrainer(chatbot)
for conversation in weather_conversations:
    list_trainer.train(conversation)

# Function to extract date from user input using SpaCy
def extract_datetime_from_input(input_text):
    doc = nlp(input_text)
    extracted_date = None
    extracted_time = None

    for ent in doc.ents:
        if ent.label_ == "DATE":
            extracted_date = parse_date(ent.text)
        elif ent.label_ == "TIME":
            extracted_time = parse_time(ent.text)

    return extracted_date, extracted_time

# Function to parse date from extracted text
def parse_date(date_str):
    try:
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            return parsed_date.date()
        else:
            return None
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

# Function to parse time from extracted text
def parse_time(time_str):
    try:
        parsed_time = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': False})
        if parsed_time:
            return parsed_time.time()
        else:
            return None
    except Exception as e:
        logging.warning(f"Failed to parse time from: {time_str}")
        return None

# Normalize city name for consistent querying
def normalize_city_name(city):
    city_parts = city.split()
    return ' '.join(part.capitalize() for part in city_parts)

# Function to fetch current weather from the database
def get_weather_from_db(location, date=None):
    with app.app_context():
        normalized_location = normalize_city_name(location)
        logging.debug(f"Normalized city name: {normalized_location}")

        query = CurrentWeather.query.filter(
            CurrentWeather.city.ilike(f'%{normalized_location}%')
        )

        if date:
            logging.debug(f"Querying for date: {date}")
            query = query.filter(CurrentWeather.date_recorded == date)
        else:
            # No date provided, fetch the latest available record
            logging.debug("No specific date provided, fetching the latest available weather data.")
            query = query.order_by(desc(CurrentWeather.date_recorded)).limit(1)

        logging.debug(f"Final Query: {query}")

        try:
            weather_data = query.first()

            if weather_data:
                response = (f"Weather in {weather_data.city} on {weather_data.date_recorded:%A %d %B %Y}:\n"
                            f"- Description: {weather_data.description.capitalize()}\n"
                            f"- Temperature: {weather_data.temperature}°C\n"
                            f"- Feels like: {weather_data.temp_min}°C to {weather_data.temp_max}°C\n"
                            f"- Humidity: {weather_data.humidity}%\n"
                            f"- Sunrise: {weather_data.sunrise}\n"
                            f"- Sunset: {weather_data.sunset}\n")
                logging.debug(f"Found weather data: {response}")
                return response
            else:
                logging.info(f"No weather data found for {location} on {date}.")
                return f"Sorry, I don't have weather data for {location} on {date}."
        except Exception as e:
            logging.error(f"Error fetching weather data for {location} on {date}: {e}")
            return f"Sorry, there was an error fetching weather data for {location} on {date}."

# Function to fetch forecast weather from the database
# Function to fetch forecast weather from the database
def get_forecast_weather_from_db(city, date, specific_time=None):
    with app.app_context():
        normalized_city = normalize_city_name(city)
        logging.debug(f"Normalized city name: {normalized_city}")

        if specific_time:
            # Query for the specific forecast time
            forecast = ForecastWeather.query.filter(
                ForecastWeather.city.ilike(f'%{normalized_city}%'),
                ForecastWeather.forecast_time == specific_time
            ).first()

            try:
                if forecast:
                    response = (f" Weather in {normalized_city} for {specific_time.strftime('%A %d %B %Y %I:%M %p')}:\n"
                                f"- Description: {forecast.description.capitalize()}\n"
                                f"- Temperature: {forecast.temp_min}°C\n")  # Assuming temp_min and temp_max are the same
                    logging.debug(f"Found forecast data: {response}")
                    return response
                else:
                    logging.debug(f"No forecast data found for {normalized_city} at {specific_time}.")
                    return f"Sorry, I don't have forecast data for {normalized_city} at {specific_time.strftime('%A %d %B %Y %I:%M %p')}."
            except Exception as e:
                logging.error(f"Error fetching forecast weather for {normalized_city} at {specific_time}: {e}")
                return f"Sorry, there was an error fetching forecast weather data for {city}."

        else:
            # For historical weather data, fetch the closest available data
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date + timedelta(days=1), datetime.min.time())

            historical_weather = ForecastWeather.query.filter(
                ForecastWeather.city.ilike(f'%{normalized_city}%'),
                ForecastWeather.forecast_time >= start_datetime,
                ForecastWeather.forecast_time < end_datetime
            ).order_by(ForecastWeather.forecast_time.asc()).first()

            try:
                if historical_weather:
                    response = (f"Weather in {normalized_city} for {date.strftime('%A %d %B %Y')} at"
                                f" {historical_weather.forecast_time.strftime('%I:%M %p')}:\n"
                                f"- Description: {historical_weather.description.capitalize()}\n"
                                f"- Temperature: {historical_weather.temp_min}°C\n"
                                f"- Feels like: {historical_weather.temp_max}°C\n")

                    logging.debug(f"Found historical weather data: {response}")
                    return response
                else:
                    logging.debug(f"No historical weather data found for {normalized_city} on {date}.")
                    return f"Sorry, I don't have historical weather data for {normalized_city} on {date.strftime('%A %d %B %Y')}."
            except Exception as e:
                logging.error(f"Error fetching historical weather for {normalized_city} on {date}: {e}")
                return f"Sorry, there was an error fetching historical weather data for {city}."



# List of specific place names to ensure recognition
specific_places = [
    "Cumbria",
    "Corfe Castle",
    "The Cotswolds",
    "Cambridge",
    "Bristol",
    "Oxford",
    "Norwich",
    "Stonehenge",
    "Watergate Bay",
    "Birmingham"
]

# Function to check if location is in specific_places
def is_specific_place(location):
    return any(location.lower() == name.lower() for name in specific_places)

# Function to generate weather response based on user query
def dynamic_weather_response(query):
    with app.app_context():
        doc = nlp(query)
        location = None
        date = None
        specific_time = None

        # Check for specific places
        for name in specific_places:
            if name.lower() in query.lower():
                location = name
                break

        # If no specific place found in query, use SpaCy entity extraction
        if not location:
            for ent in doc.ents:
                if ent.label_ in {"GPE", "LOC"}:
                    location = ent.text
                    break

        # Extract entities and log each extraction step
        for ent in doc.ents:
            logging.debug(f"Entity found: {ent.text} (Label: {ent.label_})")
            if ent.label_ in {"GPE", "LOC"}:
                location = ent.text
                logging.debug(f"Extracted location: {location}")
            elif ent.label_ == "DATE":
                date_str = ent.text
                logging.debug(f"Extracted date string: {date_str}")
                date = parse_date(date_str)
                if date:
                    logging.debug(f"Parsed date: {date}")
                else:
                    logging.warning(f"Failed to parse date from: {date_str}")
            elif ent.label_ == "TIME":
                specific_time_str = ent.text
                logging.debug(f"Extracted time string: {specific_time_str}")
                specific_time = parse_time(specific_time_str)
                if specific_time:
                    logging.debug(f"Parsed time: {specific_time}")
                else:
                    logging.warning(f"Failed to parse time from: {specific_time_str}")

        # Check for weather-related keywords
        weather_keywords = ["weather", "temperature", "forecast"]
        if any(keyword in query.lower() for keyword in weather_keywords):
            logging.debug("Weather-related keyword detected.")

            # Logic to determine weather query based on extracted entities
            if location:
                if date:
                    if specific_time:
                        specific_datetime = datetime.combine(date, specific_time)
                        if specific_datetime.date() == datetime.now().date():
                            logging.debug("Fetching specific current weather")
                            weather_response = get_weather_from_db(location)
                        elif specific_datetime.date() < datetime.now().date():
                            logging.debug("Fetching specific historical weather")
                            weather_response = get_forecast_weather_from_db(location, date, specific_datetime)
                        else:
                            logging.debug("Fetching specific forecast weather")
                            weather_response = get_forecast_weather_from_db(location, date, specific_datetime)
                    else:
                        if date == datetime.now().date():
                            logging.debug("Fetching current weather")
                            weather_response = get_weather_from_db(location)
                        elif date < datetime.now().date():
                            logging.debug("Fetching historical weather")
                            weather_response = get_forecast_weather_from_db(location, date)
                        else:
                            logging.debug("Fetching forecast weather")
                            weather_response = get_forecast_weather_from_db(location, date)
                else:
                    logging.debug("Fetching current weather (default)")
                    weather_response = get_weather_from_db(location)

                # Generate advice based on weather conditions
                if weather_response:
                    advice = generate_weather_advice(weather_response)
                    return f"{weather_response}\n\n{advice}"
                else:
                    return "Sorry, I couldn't fetch weather data for your query."

        # Fallback mechanism if no location was found
        if not location:
            logging.info("No GPE/LOC entity found, applying fallback location extraction.")
            potential_location = " ".join(
                [word for word in query.split() if word.istitle() and word.lower() not in ["Hi", "Hot"]])
            if potential_location.strip():
                location = potential_location.strip()
                logging.debug(f"Fallback location: {location}")
            else:
                logging.debug("No potential location found in query.")
                # Fallback to chatbot response
                chatbot_response = chatbot.get_response(query)

                # Convert the chatbot response to a string if it's a Statement
                if isinstance(chatbot_response, Statement):
                    response = str(chatbot_response)
                else:
                    response = chatbot_response

                logging.info(f"Chatbot response: {response}")
                return response

        # If no weather-related keyword detected, fall back to general chatbot response
        logging.info("No weather-related keyword detected, falling back to chatbot response.")
        chatbot_response = chatbot.get_response(query)

        # Convert the chatbot response to a string if it's a Statement
        if isinstance(chatbot_response, Statement):
            return str(chatbot_response)
        else:
            return chatbot_response



def generate_weather_advice(weather_response):
    if "rain" in weather_response.lower():
        return "- Don't forget your umbrella!"
    elif "sun" in weather_response.lower():
        return "- Wear sunscreen and stay hydrated!"
    elif "snow" in weather_response.lower():
        return "- Bundle up and drive safely!"
    elif "wind" in weather_response.lower():
        return "- Secure loose objects and be cautious outdoors!"
    elif "cloud" in weather_response.lower():
        return "- Expect varying cloud cover throughout the day."
    elif "fog" in weather_response.lower():
        return "- Drive with caution due to reduced visibility."
    elif "storm" in weather_response.lower():
        return "- Stay indoors and away from windows during the storm."
    else:
        return "No specific advice for current weather."



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print("WeatherBot is ready to chat! Type ':q', 'quit', or 'exit' to stop.")
    while True:
        query = input("> ")
        if query.lower() in (":q", "quit", "exit"):
            print("Goodbye!")
            break
        response = dynamic_weather_response(query)
        print(f"☀️ {response}")


