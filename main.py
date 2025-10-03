from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uvicorn

from services.nasa_power_client import NASAPowerClient
from services.location_service import LocationService
from services.weather_risk_analyzer import WeatherRiskAnalyzer

app = FastAPI(
    title="NASA Weather Risk Detection API",
    description="Personalized weather risk assessment for outdoor activities using NASA POWER data",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
nasa_client = NASAPowerClient()
location_service = LocationService()
risk_analyzer = WeatherRiskAnalyzer()

# Pydantic models for request/response
class LocationRequest(BaseModel):
    location_name: str

class LocationResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: str

class WeatherRiskRequest(BaseModel):
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    activity_type: Optional[str] = "general"

class RiskCategory(BaseModel):
    category: str
    probability: float
    threshold_value: float
    risk_level: str  # low, moderate, high, very_high
    description: str
    activity_impact: str
    confidence: float
    sample_size: int
    historical_events: int

class WeatherRiskResponse(BaseModel):
    location: dict
    date_range: dict
    risk_categories: List[RiskCategory]
    overall_risk_score: float
    recommendations: List[str]
    historical_data_years: int

@app.get("/")
async def root():
    return {
        "message": "NASA Weather Risk Detection API",
        "version": "1.0.0",
        "description": "Get personalized weather risk assessments for outdoor activities"
    }

@app.post("/api/geocode", response_model=List[LocationResponse])
async def geocode_location(request: LocationRequest):
    """
    Convert location name to coordinates using OpenStreetMap Nominatim
    """
    try:
        locations = await location_service.geocode(request.location_name)
        if not locations:
            raise HTTPException(status_code=404, detail="Location not found")
        return locations
    except ValueError as e:
        # Handle empty/invalid location names from location service
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")

@app.post("/api/weather-risk", response_model=WeatherRiskResponse)
async def assess_weather_risk(request: WeatherRiskRequest):
    """
    Assess weather risk for given location and date range using NASA POWER historical data
    """
    try:
        # Fetch historical weather data from NASA POWER
        historical_data = await nasa_client.get_historical_data(
            latitude=request.latitude,
            longitude=request.longitude,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Analyze weather risk
        risk_assessment = risk_analyzer.analyze_risk(
            historical_data=historical_data,
            target_dates=(request.start_date, request.end_date),
            activity_type=request.activity_type
        )
        
        return risk_assessment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather risk analysis error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "nasa_power": "operational",
            "location_service": "operational",
            "risk_analyzer": "operational"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)