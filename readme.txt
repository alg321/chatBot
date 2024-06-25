WeatherBot Flask Application
Overview
WeatherBot is a Flask-based web application that provides weather information and a chatbot interface for interacting with weather-related queries. It integrates with OpenWeatherMap API for fetching real-time and forecasted weather data and utilizes natural language processing (NLP) to interpret user queries.

Features
Real-time Weather Updates: Fetch current weather conditions for specific locations.
Forecasted Weather: Retrieve weather forecasts for future dates and times.
Natural Language Processing: Understand and respond to user queries about weather using SpaCy.
Interactive Chatbot: Engage users in conversations related to weather conditions.
Persistent Storage: Store weather data in a SQLite database for efficient retrieval.

How to use
1. load flask app (app.py)
2. Interact with WeatherBot
3. Upon visiting the application, you will be directed to the homepage.You can navigate to different sections of the application from here.
4. Weather Page (/weather): Navigate to the weather page to view weather information for specific cities. Select a city
from the dropdown menu or input a city name in the form to fetch weather data.
5.Chatbot Interaction (/chatbot): Interact with the WeatherBot by entering queries related to weather. Type your query
and press Enter to receive responses regarding weather conditions.

What can you ask?
General Weather Queries:
"What's the current weather in Cumbria?"
"Give me the forecast for tomorrow in Corfe Castle."
Historical Weather Data:
"What was the weather like in Corfe Castle last Friday?"
"How hot was it in The Cotswolds on June 15th?"