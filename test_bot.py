import pytest
from bot import dynamic_weather_response, parse_date, parse_time
from datetime import datetime, timedelta

# Test cases for the dynamic_weather_response function
@pytest.mark.parametrize("query,expected_location", [
    ("What's the weather in Bristol?", "Bristol"),
    ("Tell me the weather forecast for Cumbria", "Cumbria"),
    ("How's the weather in Birmingham tomorrow?", "Birmingham"),
    ("Weather forecast in Bristol for next Monday", "Bristol"),
    ("Can you give me the weather for Cumbria next weekend?", "Cumbria"),
])
def test_location_extraction(query, expected_location):
    response = dynamic_weather_response(query)
    assert expected_location.lower() in response.lower()

@pytest.mark.parametrize("query,expected_phrase", [
    ("What's the weather in Bristol?", "Weather in Bristol"),
    ("Tell me the weather forecast for Cumbria", "Weather in Cumbria"),
    ("How's the weather in Birmingham tomorrow?", "Weather in Birmingham"),
    ("Weather forecast in Bristol for next Monday", "Weather in Bristol"),
    ("Can you give me the weather for Cumbria next weekend?", "Weather in Cumbria"),
])
def test_weather_keyword_detection(query, expected_phrase):
    response = dynamic_weather_response(query)
    assert expected_phrase.lower() in response.lower()

# Test cases for date and time parsing functions
@pytest.mark.parametrize("date_str,expected_date", [
    ("today", datetime.now().date()),
    ("tomorrow", datetime.now().date() + timedelta(days=1)),
])
def test_parse_date(date_str, expected_date):
    parsed_date = parse_date(date_str)
    assert parsed_date == expected_date

@pytest.mark.parametrize("time_str,expected_time", [
    ("10 AM", datetime.strptime("10:00", "%H:%M").time()),
    ("3 PM", datetime.strptime("15:00", "%H:%M").time()),
    ("midnight", datetime.strptime("00:00", "%H:%M").time()),
])
def test_parse_time(time_str, expected_time):
    parsed_time = parse_time(time_str)
    assert parsed_time == expected_time

# Integration test cases
def test_current_weather_in_bristol():
    query = "What's the weather in Bristol today?"
    response = dynamic_weather_response(query)
    assert "Weather in Bristol" in response

def test_past_weather_in_cumbria():
    query = "What was the weather in Cumbria last Monday?"
    response = dynamic_weather_response(query)
    assert "Weather in Cumbria" in response

def test_future_forecast_in_birmingham():
    query = "What will the weather be like in Birmingham next Friday?"
    response = dynamic_weather_response(query)
    assert "Weather in Birmingham" in response

if __name__ == "__main__":
    pytest.main()
