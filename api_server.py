from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Dict, List
import uvicorn
import os
import uuid
import time

from weather_processor import WeatherProcessor
from database import WeatherDatabase

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

# Initialize weather processor and database
weather_processor = WeatherProcessor()
db = WeatherDatabase()

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
        # Try to load existing models from database
        models_loaded = weather_processor.load_models()
        if models_loaded:
            print("Loaded existing weather models from database")
        else:
            print("No existing models found. Training new models...")
            # Train new models if none exist
            df = weather_processor.load_and_preprocess_data()
            features = weather_processor.create_features(df)
            classifications = weather_processor.create_weather_classifications(df)
            weather_processor.train_models(features, classifications)
            print("New models trained and saved to database")
    except Exception as e:
        print(f"Error during startup: {e}")
        # Continue anyway - the API will still work with fallback predictions

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
    db_stats = db.get_database_stats()
    return {
        "status": "healthy", 
        "models_loaded": len(weather_processor.models) > 0,
        "database_stats": db_stats
    }

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
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    try:
        # Check cache first
        date_str = request.date.strftime("%Y-%m-%d")
        cached = db.get_cached_prediction(
            date_str, request.location.latitude, request.location.longitude, request.activity
        )
        
        if cached:
            # Log cache hit
            db.log_user_query(
                session_id, 
                {"type": "cache_hit", "date": date_str, "activity": request.activity},
                cached,
                time.time() - start_time
            )
            
            # Convert cached data to response format
            return WeatherResponse(
                date=request.date,
                location=request.location,
                activity=request.activity,
                prediction=ActivityRecommendation(**cached)
            )
        
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
        
        # Prepare response
        prediction_result = {
            "overall_risk_score": overall_risk_score,
            "risk_level": overall_risk,
            "recommendations": recommendations,
            "conditions": {k: v.__dict__ for k, v in condition_predictions.items()}
        }
        
        # Cache the prediction
        db.cache_prediction(date_str, request.location.latitude, request.location.longitude, 
                           request.activity, prediction_result)
        
        # Log the query
        response_time = time.time() - start_time
        db.log_user_query(
            session_id,
            {
                "date": date_str,
                "latitude": request.location.latitude,
                "longitude": request.location.longitude,
                "activity": request.activity
            },
            prediction_result,
            response_time
        )
        
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
        # Log error
        db.log_user_query(
            session_id,
            {"error": str(e), "date": request.date.strftime("%Y-%m-%d"), "activity": request.activity},
            None,
            time.time() - start_time
        )
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

@app.get("/models/info")
async def get_models_info():
    """Get information about stored ML models"""
    models = db.get_model_info()
    stats = db.get_database_stats()
    
    return {
        "models": models,
        "database_stats": stats,
        "total_models": len(models)
    }

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get basic analytics about API usage"""
    stats = db.get_database_stats()
    
    return {
        "total_predictions": stats.get('weather_predictions', 0),
        "total_queries": stats.get('user_queries', 0),
        "models_count": stats.get('ml_models', 0),
        "database_size_mb": stats.get('db_size_mb', 0)
    }

if __name__ == "__main__":
    # Initialize database
    print("Initializing WeatherWise database...")
    db = WeatherDatabase()
    
    # Run the server
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )