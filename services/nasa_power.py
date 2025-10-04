import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from config import Config

class NASAPowerService:
    """Service to fetch weather data from NASA POWER API"""
    
    def __init__(self):
        self.base_url = Config.NASA_POWER_BASE_URL
        self.parameters = Config.WEATHER_PARAMETERS
    
    def get_weather_data(self, latitude: float, longitude: float, 
                        start_date: str, end_date: str) -> Optional[Dict]:
        """
        Fetch weather data from NASA POWER API
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            
        Returns:
            Dictionary containing weather data or None if failed
        """
        try:
            params = {
                'parameters': ','.join(self.parameters),
                'community': 'AG',
                'longitude': longitude,
                'latitude': latitude,
                'start': start_date,
                'end': end_date,
                'format': 'JSON'
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' in data and 'parameter' in data['properties']:
                return self._process_weather_data(data['properties']['parameter'])
            else:
                print(f"Unexpected API response structure: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except Exception as e:
            print(f"Error processing weather data: {e}")
            return None
    
    def _process_weather_data(self, raw_data: Dict) -> Dict:
        """Process raw NASA POWER data into a structured format"""
        processed_data = {
            'temperature': [],
            'precipitation': [],
            'wind_speed': [],
            'humidity': [],
            'pressure': [],
            'specific_humidity': [],
            'dates': []
        }
        
        # Get all dates from the first parameter
        first_param = next(iter(raw_data.values()))
        dates = list(first_param.keys())
        
        for date in dates:
            processed_data['dates'].append(date)
            
            # Extract values for each parameter with validation
            temp = raw_data.get('T2M', {}).get(date, None)
            precip = raw_data.get('PRECTOTCORR', {}).get(date, None)
            wind = raw_data.get('WS2M', {}).get(date, None)
            humidity = raw_data.get('RH2M', {}).get(date, None)
            pressure = raw_data.get('PS', {}).get(date, None)
            spec_humidity = raw_data.get('QV2M', {}).get(date, None)
            
            # Validate and clean data - NASA POWER sometimes returns invalid negative values
            processed_data['temperature'].append(
                temp if temp is not None and -100 < temp < 60 else None
            )
            processed_data['precipitation'].append(
                precip if precip is not None and precip >= 0 and precip < 1000 else None
            )
            processed_data['wind_speed'].append(
                wind if wind is not None and wind >= 0 and wind < 200 else None
            )
            processed_data['humidity'].append(
                humidity if humidity is not None and 0 <= humidity <= 100 else None
            )
            processed_data['pressure'].append(
                pressure if pressure is not None and pressure > 0 and pressure < 1100 else None
            )
            processed_data['specific_humidity'].append(
                spec_humidity if spec_humidity is not None and spec_humidity >= 0 else None
            )
        
        return processed_data
    
    def get_historical_data(self, latitude: float, longitude: float, 
                          days_back: int = 30) -> Optional[Dict]:
        """Get historical weather data for the past N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        return self.get_weather_data(latitude, longitude, start_str, end_str)
    
    def get_yearly_patterns(self, latitude: float, longitude: float, 
                           year: int = None) -> Optional[Dict]:
        """Get weather patterns for a specific year or current year"""
        if year is None:
            year = datetime.now().year - 1  # Use last year for complete data
        
        start_date = f"{year}0101"
        end_date = f"{year}1231"
        
        return self.get_weather_data(latitude, longitude, start_date, end_date)
    
    def analyze_weather_conditions(self, weather_data: Dict) -> Dict:
        """Analyze weather data to determine extreme conditions"""
        if not weather_data or not weather_data.get('temperature'):
            return {}
        
        analysis = {
            'very_hot_days': 0,
            'very_cold_days': 0,
            'very_windy_days': 0,
            'very_wet_days': 0,
            'very_uncomfortable_days': 0,
            'total_days': len(weather_data['temperature']),
            'avg_temperature': 0,
            'avg_precipitation': 0,
            'avg_wind_speed': 0,
            'avg_humidity': 0,
            'valid_data_points': 0
        }
        
        # Filter out None and invalid values
        temps = [t for t in weather_data['temperature'] if t is not None and -100 < t < 60]
        precip = [p for p in weather_data['precipitation'] if p is not None and p >= 0]
        winds = [w for w in weather_data['wind_speed'] if w is not None and w >= 0]
        humidity = [h for h in weather_data['humidity'] if h is not None and 0 <= h <= 100]
        
        # Track how much valid data we have
        analysis['valid_data_points'] = len(temps)
        
        if temps:
            analysis['avg_temperature'] = sum(temps) / len(temps)
            analysis['very_hot_days'] = len([t for t in temps if t > 35])  # >35°C
            analysis['very_cold_days'] = len([t for t in temps if t < 0])   # <0°C
        
        if precip:
            analysis['avg_precipitation'] = sum(precip) / len(precip)
            analysis['very_wet_days'] = len([p for p in precip if p > 10])  # >10mm
        
        if winds:
            analysis['avg_wind_speed'] = sum(winds) / len(winds)
            analysis['very_windy_days'] = len([w for w in winds if w > 15])  # >15 m/s
        
        if humidity:
            analysis['avg_humidity'] = sum(humidity) / len(humidity)
        
        # Calculate uncomfortable days (high temp + high humidity or extreme conditions)
        uncomfortable_count = 0
        for i in range(len(weather_data['dates'])):
            temp = weather_data['temperature'][i]
            hum = weather_data['humidity'][i]
            wind = weather_data['wind_speed'][i]
            rain = weather_data['precipitation'][i]
            
            # Only count if we have valid data
            if (temp and hum and temp > 30 and hum > 80 and 0 <= hum <= 100) or \
               (temp and temp > 40 and -100 < temp < 60) or \
               (wind and wind > 20 and wind >= 0) or \
               (rain and rain > 20 and rain >= 0):
                uncomfortable_count += 1
        
        analysis['very_uncomfortable_days'] = uncomfortable_count
        
        # Add data quality indicator
        if analysis['valid_data_points'] < analysis['total_days'] * 0.5:
            analysis['data_quality'] = 'poor'
        elif analysis['valid_data_points'] < analysis['total_days'] * 0.8:
            analysis['data_quality'] = 'moderate'
        else:
            analysis['data_quality'] = 'good'
        
        return analysis