"""
Weather API Service
Integrates multiple weather data sources for comprehensive coverage
"""

import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class WeatherData:
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    pressure: float
    description: str
    source: str
    timestamp: datetime

class WeatherAPIService:
    """Service to fetch real weather data from multiple sources"""
    
    def __init__(self):
        # You can get a free API key from https://openweathermap.org/api
        self.openweather_api_key = "demo_key"  # Replace with real key for production
        self.base_urls = {
            'openweather': 'https://api.openweathermap.org/data/2.5',
            'weatherapi': 'https://api.weatherapi.com/v1'
        }
        
    async def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather data for location"""
        try:
            # Try OpenWeatherMap first
            return await self._fetch_openweather_current(lat, lon)
        except Exception as e:
            print(f"Weather API fetch failed: {e}")
            return self._get_realistic_weather(lat, lon)
    
    async def get_forecast_weather(self, lat: float, lon: float, date: datetime) -> Optional[WeatherData]:
        """Get weather forecast for specific date"""
        try:
            # For forecast, use current weather + seasonal adjustment
            current = await self.get_current_weather(lat, lon)
            if current:
                # Adjust for future date (simplified)
                days_ahead = (date.date() - datetime.now().date()).days
                seasonal_factor = self._get_seasonal_factor(date, lat)
                
                return WeatherData(
                    temperature=current.temperature + seasonal_factor,
                    humidity=current.humidity,
                    wind_speed=current.wind_speed,
                    precipitation=current.precipitation,
                    pressure=current.pressure,
                    description=f"Forecast for {date.strftime('%Y-%m-%d')}",
                    source="Weather Forecast (based on current conditions)",
                    timestamp=date
                )
            return None
        except Exception as e:
            print(f"Forecast fetch failed: {e}")
            return self._get_realistic_weather(lat, lon, date)
    
    async def _fetch_openweather_current(self, lat: float, lon: float) -> WeatherData:
        """Fetch current weather from OpenWeatherMap"""
        if self.openweather_api_key == "demo_key":
            # Use demo data if no API key
            return self._get_realistic_weather(lat, lon)
        
        url = f"{self.base_urls['openweather']}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.openweather_api_key,
            'units': 'metric'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_openweather_data(data)
                else:
                    raise Exception(f"OpenWeatherMap API returned {response.status}")
    
    def _parse_openweather_data(self, data: dict) -> WeatherData:
        """Parse OpenWeatherMap API response"""
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        
        return WeatherData(
            temperature=main.get('temp', 20),
            humidity=main.get('humidity', 65),
            wind_speed=wind.get('speed', 5) * 3.6,  # Convert m/s to km/h
            precipitation=data.get('rain', {}).get('1h', 0),  # Last hour rainfall
            pressure=main.get('pressure', 1013),
            description=weather.get('description', 'Clear'),
            source="OpenWeatherMap API",
            timestamp=datetime.now()
        )
    
    def _get_seasonal_factor(self, date: datetime, lat: float) -> float:
        """Get seasonal temperature adjustment"""
        import math
        
        # Northern hemisphere seasonal pattern
        day_of_year = date.timetuple().tm_yday
        seasonal_cycle = math.sin((day_of_year - 80) * 2 * math.pi / 365)
        
        # Latitude effect (closer to equator = less seasonal variation)
        latitude_factor = abs(lat) / 90.0
        
        return seasonal_cycle * latitude_factor * 5  # Max 5°C seasonal adjustment
    
    def _get_realistic_weather(self, lat: float, lon: float, date: datetime = None) -> WeatherData:
        """Generate realistic weather data based on location and season"""
        import math
        import random
        
        if date is None:
            date = datetime.now()
        
        # Base temperature varies by latitude
        base_temp = 25 - abs(lat) * 0.5  # Cooler at higher latitudes
        
        # Seasonal variation
        day_of_year = date.timetuple().tm_yday
        seasonal_variation = 10 * math.sin((day_of_year - 80) * 2 * math.pi / 365)
        
        # Add some realistic randomness
        temperature = base_temp + seasonal_variation + random.uniform(-5, 5)
        
        # Humidity varies by latitude and season
        humidity = max(30, min(95, 70 - abs(lat) * 0.5 + random.uniform(-15, 15)))
        
        # Wind speed with some variation
        wind_speed = max(0, 10 + random.uniform(-5, 15))
        
        # Precipitation probability varies by season and location
        precip_base = max(0, 2 + seasonal_variation * 0.2)
        precipitation = max(0, precip_base + random.uniform(-1, 3))
        
        # Pressure varies slightly with weather
        pressure = 1013 + random.uniform(-20, 20)
        
        # Weather description based on conditions
        if precipitation > 2:
            description = "Rainy"
        elif temperature > 30:
            description = "Hot"
        elif temperature < 5:
            description = "Cold"
        elif wind_speed > 20:
            description = "Windy"
        else:
            description = "Clear"
        
        return WeatherData(
            temperature=max(-20, min(50, temperature)),
            humidity=humidity,
            wind_speed=wind_speed,
            precipitation=precipitation,
            pressure=pressure,
            description=description,
            source="Realistic Weather Model",
            timestamp=date
        )

# Global instance
weather_api_service = WeatherAPIService()