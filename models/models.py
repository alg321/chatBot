from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app import db
from datetime import datetime


class CurrentWeather(db.Model):
    __tablename__ = 'current_weather'
    id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    main = Column(String(50))
    description = Column(String(100))
    icon = Column(String(10))
    temperature = Column(Float)
    humidity = Column(Float)
    sunrise = Column(String(50))
    sunset = Column(String(50))
    temp_min = Column(Float)
    temp_max = Column(Float)
    date_recorded = Column(DateTime, default=datetime.utcnow)

    forecasts = relationship("ForecastWeather", back_populates="current_weather")


class ForecastWeather(db.Model):
    __tablename__ = 'forecast_weather'
    id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    forecast_time = Column(DateTime)
    temp_min = Column(Float)
    temp_max = Column(Float)
    description = Column(String(100))
    icon = Column(String(10))
    current_weather_id = Column(Integer, ForeignKey('current_weather.id'))
    date_recorded = Column(DateTime, default=datetime.utcnow)

    current_weather = relationship("CurrentWeather", back_populates="forecasts")
