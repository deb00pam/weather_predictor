from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Dict, List
import uvicorn
import os

from weather_processor import WeatherProcessor

app = FastAPI(
    title="WeatherWise API",
    description="Intelligent weather risk assessment for outdoor activities",
    version="1.0.0"
)

# Add CORS middleware for frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize weather processor
weather_processor = WeatherProcessor()

# Activity-specific risk thresholds and recommendations
ACTIVITY_PROFILES = {
    "hiking": {
        "name": "Hiking/Trekking",
        "risk_weights": {
            "very_hot": 0.9,
            "very_cold": 0.7,
            "very_wet": 0.8,
            "very_windy": 0.6,
            "very_uncomfortable": 0.8
        },
        "recommendations": {
            "very_hot": "Avoid midday hiking. Start early morning or late evening.",
            "very_cold": "Bring warm layers and check for ice on trails.",
            "very_wet": "Trails may be muddy/slippery. Consider waterproof gear.",
            "very_windy": "Be cautious near ridges and exposed areas.",
            "very_uncomfortable": "High heat index. Bring extra water and take frequent breaks."
        }
    },
    "fishing": {
        "name": "Fishing",
        "risk_weights": {
            "very_hot": 0.5,
            "very_cold": 0.6,
            "very_wet": 0.4,
            "very_windy": 0.9,
            "very_uncomfortable": 0.6
        },
        "recommendations": {
            "very_hot": "Fish during cooler parts of the day.",
            "very_cold": "Fish may be less active. Try deeper waters.",
            "very_wet": "Light rain can improve fishing, but heavy rain may be dangerous.",
            "very_windy": "High winds make casting difficult and water choppy.",
            "very_uncomfortable": "Seek shade and stay hydrated."
        }
    },
    "camping": {
        "name": "Camping",
        "risk_weights": {
            "very_hot": 0.7,
            "very_cold": 0.9,
            "very_wet": 0.9,
            "very_windy": 0.7,
            "very_uncomfortable": 0.8
        },
        "recommendations": {
            "very_hot": "Ensure adequate ventilation and shade.",
            "very_cold": "Check sleeping bag rating and bring extra insulation.",
            "very_wet": "Waterproof gear essential. Check tent seams.",
            "very_windy": "Secure all equipment and choose sheltered campsite.",
            "very_uncomfortable": "Consider postponing or choosing climate-controlled accommodation."
        }
    },
    "outdoor_sports": {
        "name": "Outdoor Sports",
        "risk_weights": {
            "very_hot": 0.8,
            "very_cold": 0.5,
            "very_wet": 0.8,
            "very_windy": 0.7,
            "very_uncomfortable": 0.9
        },
        "recommendations": {
            "very_hot": "Schedule during cooler hours. Increase hydration.",
            "very_cold": "Warm up thoroughly and dress in layers.",
            "very_wet": "Slippery conditions. Consider indoor alternatives.",
            "very_windy": "Wind may affect ball sports and balance activities.",
            "very_uncomfortable": "High risk of heat exhaustion during physical activity."
        }
    },
    "beach_vacation": {
        "name": "Beach/Vacation",
        "risk_weights": {
            "very_hot": 0.4,
            "very_cold": 0.8,
            "very_wet": 0.7,
            "very_windy": 0.3,
            "very_uncomfortable": 0.6
        },
        "recommendations": {
            "very_hot": "Perfect beach weather! Don't forget sunscreen.",
            "very_cold": "Too cold for swimming. Consider indoor activities.",
            "very_wet": "Beach activities limited. Plan indoor alternatives.",
            "very_windy": "Great for wind sports but protect belongings from sand.",
            "very_uncomfortable": "Seek air conditioning during peak hours."
        }
    }
}

# Pydantic models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = None

class WeatherRequest(BaseModel):
    date: date
    location: LocationRequest
    activity: Optional[str] = "general"

class WeatherPrediction(BaseModel):
    probability: float
    risk_level: str
    binary_prediction: bool

class ActivityRecommendation(BaseModel):
    overall_risk_score: float
    risk_level: str
    recommendations: List[str]
    conditions: Dict[str, WeatherPrediction]

class WeatherResponse(BaseModel):
    date: date
    location: LocationRequest
    activity: str
    prediction: ActivityRecommendation

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    try:
        # Try to load existing models
        weather_processor.load_models()
        print("Loaded existing weather models")
    except:
        print("No existing models found. Training new models...")
        # Train new models if none exist
        df = weather_processor.load_and_preprocess_data()
        features = weather_processor.create_features(df)
        classifications = weather_processor.create_weather_classifications(df)
        weather_processor.train_models(features, classifications)
        weather_processor.save_models()
        print("New models trained and saved")

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "WeatherWise API is running!",
        "version": "1.0.0",
        "endpoints": [
            "/predict-weather",
            "/activities",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": len(weather_processor.models) > 0}

@app.get("/activities")
async def get_activities():
    """Get list of supported activities"""
    return {
        "activities": {k: v["name"] for k, v in ACTIVITY_PROFILES.items()},
        "total": len(ACTIVITY_PROFILES)
    }

@app.post("/predict-weather", response_model=WeatherResponse)
async def predict_weather(request: WeatherRequest):
    """Predict weather risks for a specific date, location, and activity"""
    try:
        # Get raw weather predictions
        predictions = weather_processor.predict_weather_risks(
            datetime.combine(request.date, datetime.min.time())
        )
        
        # Get activity profile
        activity_profile = ACTIVITY_PROFILES.get(request.activity, {
            "name": "General Activity",
            "risk_weights": {k: 0.7 for k in predictions.keys()},
            "recommendations": {k: f"Monitor {k.replace('_', ' ')} conditions." for k in predictions.keys()}
        })
        
        # Calculate activity-specific risk score
        total_weighted_risk = 0
        total_weight = 0
        recommendations = []
        
        for condition, pred in predictions.items():
            weight = activity_profile["risk_weights"].get(condition, 0.5)
            total_weighted_risk += pred["probability"] * weight
            total_weight += weight
            
            # Add recommendations for high-risk conditions
            if pred["probability"] > 0.5:
                rec = activity_profile["recommendations"].get(condition, f"Monitor {condition}")
                recommendations.append(rec)
        
        overall_risk_score = total_weighted_risk / total_weight if total_weight > 0 else 0.5
        
        # Convert predictions to response format
        condition_predictions = {
            condition: WeatherPrediction(**pred) for condition, pred in predictions.items()
        }
        
        # Determine overall risk level
        if overall_risk_score < 0.3:
            overall_risk = "low"
        elif overall_risk_score < 0.6:
            overall_risk = "medium"
        elif overall_risk_score < 0.8:
            overall_risk = "high"
        else:
            overall_risk = "very_high"
        
        # Add general recommendation if no specific ones
        if not recommendations:
            recommendations.append("Conditions look good for your planned activity!")
        
        return WeatherResponse(
            date=request.date,
            location=request.location,
            activity=request.activity,
            prediction=ActivityRecommendation(
                overall_risk_score=overall_risk_score,
                risk_level=overall_risk,
                recommendations=recommendations,
                conditions=condition_predictions
            )
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/predict-weather-simple")
async def predict_weather_simple(
    date_str: str = Query(..., description="Date in YYYY-MM-DD format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    activity: str = Query("general", description="Activity type")
):
    """Simple GET endpoint for weather prediction"""
    try:
        request_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        location = LocationRequest(latitude=lat, longitude=lon)
        request = WeatherRequest(date=request_date, location=location, activity=activity)
        
        return await predict_weather(request)
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/location-info")
async def get_location_info(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """Get location information (placeholder for geocoding service)"""
    # This would integrate with a real geocoding service in production
    return {
        "latitude": lat,
        "longitude": lon,
        "location_name": f"Location ({lat:.2f}, {lon:.2f})",
        "timezone": "UTC",
        "elevation": 100  # Placeholder
    }

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )