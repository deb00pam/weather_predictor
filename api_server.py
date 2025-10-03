from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Dict, List
import uvicorn
import os
import uuid
import time
import requests

from weather_processor import WeatherProcessor
from database import WeatherDatabase
from nasa_data_service import nasa_service
from weather_api_service import weather_api_service

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

# Geocoding models
class GeocodeRequest(BaseModel):
    location: str

class GeocodeResponse(BaseModel):
    success: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    display_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    error: Optional[str] = None

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
    """Simple GET endpoint for weather prediction using real NASA data"""
    try:
        request_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        location = LocationRequest(latitude=lat, longitude=lon)
        request = WeatherRequest(date=request_date, location=location, activity=activity)
        
        # Use the NASA-enhanced prediction instead of basic prediction
        return await predict_weather_nasa(request)
    
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

@app.post("/geocode", response_model=GeocodeResponse)
async def geocode_location(request: GeocodeRequest):
    """Geocode a location string to get latitude and longitude coordinates"""
    try:
        # Use OpenStreetMap Nominatim API
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': request.location,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        # Add a proper User-Agent header as required by Nominatim
        headers = {
            'User-Agent': 'WeatherWise-App/1.0 (Weather Prediction Application)'
        }
        
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            location_data = data[0]
            return GeocodeResponse(
                success=True,
                latitude=float(location_data['lat']),
                longitude=float(location_data['lon']),
                display_name=location_data.get('display_name', ''),
                city=location_data.get('address', {}).get('city') or 
                     location_data.get('address', {}).get('town') or 
                     location_data.get('address', {}).get('village'),
                country=location_data.get('address', {}).get('country')
            )
        else:
            return GeocodeResponse(
                success=False,
                error=f"Location '{request.location}' not found"
            )
            
    except requests.RequestException as e:
        return GeocodeResponse(
            success=False,
            error=f"Geocoding service error: {str(e)}"
        )
    except Exception as e:
        return GeocodeResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

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

@app.get("/nasa/data-sources")
async def get_nasa_data_sources():
    """Get information about NASA Earth observation data sources"""
    return nasa_service.get_data_sources_info()

@app.post("/nasa/predict-weather", response_model=WeatherResponse)
async def predict_weather_nasa(request: WeatherRequest):
    """Predict weather risks using real NASA satellite data and weather APIs"""
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    try:
        # Try multiple data sources for comprehensive coverage
        nasa_data = None
        weather_data = None
        location_features = None
        data_sources = []
        
        # 1. Try NASA POWER satellite data first
        try:
            nasa_data = await nasa_service.get_weather_data(
                request.location.latitude, 
                request.location.longitude, 
                datetime.combine(request.date, datetime.min.time())
            )
            if nasa_data:
                data_sources.append(nasa_data.source)
                print(f"✅ Got NASA data: {nasa_data.source}")
        except Exception as e:
            print(f"⚠️ NASA data fetch failed: {e}")
        
        # 2. Try real-time weather API data
        try:
            target_date = datetime.combine(request.date, datetime.min.time())
            if target_date.date() == datetime.now().date():
                # Current day - use current weather
                weather_data = await weather_api_service.get_current_weather(
                    request.location.latitude, request.location.longitude
                )
            else:
                # Future date - use forecast
                weather_data = await weather_api_service.get_forecast_weather(
                    request.location.latitude, request.location.longitude, target_date
                )
            
            if weather_data:
                data_sources.append(weather_data.source)
                print(f"✅ Got weather API data: {weather_data.source}")
        except Exception as e:
            print(f"⚠️ Weather API fetch failed: {e}")
        
        # 3. Combine data sources or use best available
        if nasa_data and weather_data:
            # Use NASA data as primary, weather API as supplementary
            location_features = {
                'temp_max': nasa_data.temperature + 5,  # Estimate daily max
                'temp_min': nasa_data.temperature - 5,  # Estimate daily min
                'rain': max(nasa_data.precipitation, weather_data.precipitation),
                'wind_speed': (nasa_data.wind_speed + weather_data.wind_speed) / 2,
                'humidity': (nasa_data.humidity + weather_data.humidity) / 2,
                'pressure': weather_data.pressure,  # Use real-time pressure
                'cloud_cover': nasa_data.cloud_cover,
                'data_source': f"NASA + {weather_data.source}"
            }
        elif nasa_data:
            # Use NASA data only
            location_features = {
                'temp_max': nasa_data.temperature + 5,
                'temp_min': nasa_data.temperature - 5,
                'rain': nasa_data.precipitation,
                'wind_speed': nasa_data.wind_speed,
                'humidity': nasa_data.humidity,
                'pressure': nasa_data.atmospheric_pressure,
                'cloud_cover': nasa_data.cloud_cover,
                'data_source': nasa_data.source
            }
        elif weather_data:
            # Use weather API data only
            location_features = {
                'temp_max': weather_data.temperature + 3,
                'temp_min': weather_data.temperature - 3,
                'rain': weather_data.precipitation,
                'wind_speed': weather_data.wind_speed,
                'humidity': weather_data.humidity,
                'pressure': weather_data.pressure,
                'cloud_cover': 50,  # Default
                'data_source': weather_data.source
            }
        else:
            # Fallback to location-based realistic weather
            print("🔄 Using fallback weather modeling...")
            location_features = None
        
        print(f"🌍 Using weather data: {location_features.get('data_source', 'Fallback model') if location_features else 'Fallback model'}")
        
        # Get raw weather predictions using real data
        predictions = weather_processor.predict_weather_risks(
            datetime.combine(request.date, datetime.min.time()),
            location_features
        )
        
        # Get activity profile
        activity_profile = ACTIVITY_PROFILES.get(request.activity, ACTIVITY_PROFILES["hiking"])
        
        # Calculate activity-specific risk
        overall_risk = 0
        recommendations = []
        detailed_conditions = {}
        
        for condition, prediction_data in predictions.items():
            # Extract probability from the prediction data
            if isinstance(prediction_data, dict):
                probability = prediction_data.get('probability', 0.5)
            else:
                probability = float(prediction_data)  # Fallback for old format
            
            weight = activity_profile["risk_weights"].get(condition, 0.5)
            risk_contribution = probability * weight
            overall_risk += risk_contribution
            
            # Add recommendation if risk is significant
            if probability > 0.3:  # 30% threshold
                recommendations.append(activity_profile["recommendations"][condition])
            
            # Create detailed condition info
            detailed_conditions[condition] = WeatherPrediction(
                probability=probability,
                risk_level="high" if probability > 0.7 else "medium" if probability > 0.4 else "low",
                binary_prediction=probability > 0.5
            )
        
        # Normalize overall risk
        overall_risk = min(overall_risk / len(predictions), 1.0)
        
        # Determine risk level
        if overall_risk > 0.7:
            risk_level = "very_high"
        elif overall_risk > 0.5:
            risk_level = "high"
        elif overall_risk > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Add data source info to recommendations
        if location_features and location_features.get('data_source'):
            recommendations.insert(0, f"🛰️ Using {location_features['data_source']} from {request.date}")
            if len(data_sources) > 1:
                recommendations.insert(1, f"📊 Combined data from: {', '.join(data_sources)}")
        
        # Add actual weather conditions to recommendations
        if location_features:
            weather_summary = f"🌡️ {location_features.get('temp_min', 15):.1f}°C - {location_features.get('temp_max', 25):.1f}°C, "
            weather_summary += f"💨 {location_features.get('wind_speed', 10):.1f} km/h, "
            weather_summary += f"💧 {location_features.get('humidity', 65):.0f}% humidity"
            if location_features.get('rain', 0) > 1:
                weather_summary += f", 🌧️ {location_features.get('rain', 0):.1f}mm rain"
            recommendations.insert(-1 if recommendations else 0, weather_summary)
        
        # Create activity recommendation
        activity_recommendation = ActivityRecommendation(
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            recommendations=recommendations,
            conditions=detailed_conditions
        )
        
        # Log NASA query with data source info
        db.log_user_query(
            session_id,
            {
                "endpoint": "nasa/predict-weather",
                "date": request.date.strftime("%Y-%m-%d"),
                "lat": request.location.latitude,
                "lon": request.location.longitude,
                "activity": request.activity,
                "location_name": request.location.location_name,
                "nasa_data_available": nasa_data is not None,
                "weather_api_available": weather_data is not None,
                "data_sources": data_sources,
                "final_data_source": location_features.get('data_source', 'fallback') if location_features else 'fallback'
            },
            {
                "overall_risk_score": overall_risk,
                "risk_level": risk_level,
                "recommendations": recommendations,
                "conditions": {k: v.dict() for k, v in detailed_conditions.items()},
                "weather_conditions": location_features
            },
            time.time() - start_time
        )
        
        return WeatherResponse(
            date=request.date,
            location=request.location,
            activity=request.activity,
            prediction=activity_recommendation
        )
        
    except Exception as e:
        # Log error
        db.log_user_query(
            session_id,
            {"error": str(e), "endpoint": "nasa/predict-weather"},
            {},
            time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"NASA prediction failed: {str(e)}")

# Direct weather parameters prediction model
class DirectWeatherRequest(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    pressure: float
    activity: str = "general"

class DirectWeatherResponse(BaseModel):
    prediction: Dict[str, float]
    activity_risk: str
    recommendation: str
    timestamp: str

@app.post("/predict", response_model=DirectWeatherResponse)
async def predict_direct(request: DirectWeatherRequest):
    """Direct prediction using weather parameters"""
    try:
        # Create a location_features dict from the input parameters
        from datetime import datetime, date
        today = date.today()
        
        location_features = {
            'temp_max': request.temperature + 2,  # Estimate daily max
            'temp_min': request.temperature - 2,  # Estimate daily min
            'temp_avg': request.temperature,
            'temp_range': 4,
            'rain': 0,  # Default for now
            'wind_speed': request.wind_speed,
            'humidity': request.humidity,
            'month': today.month,
            'day_of_year': today.timetuple().tm_yday,
            'season': ((today.month - 1) // 3) % 4
        }
        
        # Use weather processor to make predictions
        predictions_raw = weather_processor.predict_weather_risks(today, location_features)
        
        # Convert to simple probability dict
        predictions = {}
        for condition, pred_data in predictions_raw.items():
            predictions[condition] = pred_data['probability']
        
        # Calculate activity-specific risk - handle missing 'general' activity
        if request.activity not in ACTIVITY_PROFILES:
            # Default to hiking if activity not found
            activity_profile = ACTIVITY_PROFILES["hiking"]
        else:
            activity_profile = ACTIVITY_PROFILES[request.activity]
        
        # Calculate overall risk score
        risk_score = 0.0
        recommendations = []
        
        for condition, probability in predictions.items():
            weight = activity_profile["risk_weights"].get(condition, 0.5)
            risk_score += probability * weight
            
            if probability > 0.5:  # High risk threshold
                rec = activity_profile["recommendations"].get(condition, f"High {condition} probability")
                recommendations.append(rec)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Get main recommendation
        if recommendations:
            main_recommendation = recommendations[0]
        else:
            main_recommendation = "Weather conditions are favorable for this activity."
        
        return DirectWeatherResponse(
            prediction=predictions,
            activity_risk=risk_level,
            recommendation=main_recommendation,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Prediction error: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

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