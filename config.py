import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # NASA POWER API Configuration
    NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Weather parameters to fetch from NASA POWER
    WEATHER_PARAMETERS = [
        'T2M',      # Temperature at 2 Meters
        'PRECTOTCORR',  # Precipitation Corrected
        'WS2M',     # Wind Speed at 2 Meters
        'RH2M',     # Relative Humidity at 2 Meters
        'PS',       # Surface Pressure
        'QV2M'      # Specific Humidity at 2 Meters
    ]
    
    @staticmethod
    def validate_config():
        """Validate that required environment variables are set"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True