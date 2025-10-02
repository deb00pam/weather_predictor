# WeatherWise - Intelligent Weather Prediction System

## 🌤️ Overview
WeatherWise is an AI-powered weather risk assessment platform that provides **activity-specific** weather predictions for outdoor planning. Instead of generic weather forecasts, it tells you the likelihood of adverse conditions for your specific activity (hiking, fishing, camping, etc.).

## 🎯 Problem Statement (Hackathon)
*"If you're planning an outdoor event—like a vacation, a hike on a trail, or fishing on a lake—it would be good to know the chances of adverse weather for the time and location you are considering."*

## ✅ Current Status - Python Backend COMPLETE

### 📊 What's Working
- ✅ **Weather Data Processing**: Enhanced ML pipeline with 5 weather classifications
- ✅ **Machine Learning Models**: Trained classifiers for weather risk prediction
- ✅ **FastAPI Backend**: REST API with activity-specific risk assessment
- ✅ **Activity Profiles**: Customized risk weights for different activities
- ✅ **Performance**: ~2 second response times with ML predictions

### 🔮 Weather Classifications
- **Very Hot**: Temperature extremes affecting comfort
- **Very Cold**: Low temperatures impacting safety
- **Very Wet**: Heavy rainfall conditions  
- **Very Windy**: High wind speeds affecting activities
- **Very Uncomfortable**: Heat index-based discomfort levels

### 🎯 Activity Types Supported
- **Hiking/Trekking**: Prioritizes temperature extremes and trail conditions
- **Fishing**: Emphasizes wind conditions and water safety
- **Camping**: Focuses on overnight temperature and weather protection
- **Outdoor Sports**: Balances performance and safety factors
- **Beach/Vacation**: Optimized for recreational activities

## 🚀 API Endpoints

### Health Check
```
GET /health
```

### Get Activities
```
GET /activities
```

### Weather Prediction (Simple)
```
GET /predict-weather-simple?date_str=2024-10-15&lat=40.7128&lon=-74.0060&activity=hiking
```

### Weather Prediction (Detailed)
```
POST /predict-weather
{
  "date": "2024-10-15",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_name": "New York City"
  },
  "activity": "hiking"
}
```

## 🛠️ Technology Stack

### Backend (COMPLETED ✅)
- **Python 3.12**: Core language
- **FastAPI**: Modern web framework
- **scikit-learn**: Machine learning models
- **pandas/numpy**: Data processing
- **uvicorn**: ASGI server

### Planned Frontend Stack
- **Desktop**: Tauri (Rust + HTML/CSS/JS)
- **Mobile**: React Native (iOS/Android)
- **Web**: Marketing landing page with animations

## 📦 Installation & Setup

### Prerequisites
- Python 3.12+
- pip

### Quick Start
```bash
# 1. Install dependencies
pip install fastapi uvicorn pandas scikit-learn joblib pydantic python-multipart requests

# 2. Train models (first time only)
python weather_processor.py

# 3. Start API server
python api_server.py

# 4. Test the system
python demo.py

# 5. View API docs
# Open browser to: http://localhost:8000/docs
```

## 📁 Project Structure
```
weather_predictor/
├── weather_predictions.ipynb    # Original analysis notebook
├── weather.csv                  # Historical weather data (25k+ records)
├── weather_processor.py         # ML pipeline & model training
├── api_server.py               # FastAPI backend server
├── demo.py                     # Comprehensive demo script
├── test_api.py                 # API testing utilities
├── requirements.txt            # Python dependencies
├── models/                     # Trained ML models (auto-generated)
│   ├── scaler.pkl
│   ├── very_hot_model.pkl
│   ├── very_cold_model.pkl
│   ├── very_wet_model.pkl
│   ├── very_windy_model.pkl
│   └── very_uncomfortable_model.pkl
└── README.md                   # This file
```

## 🎮 Demo Features

Run `python demo.py` to see:
- **Activity-specific risk assessment** for different locations
- **Real-time API performance** testing
- **Risk level comparison** across activity types
- **Interactive examples** with recommendations

## 🌟 Key Features

### 🧠 Smart Activity Assessment
- Each activity has **custom risk weights** for different weather conditions
- **Personalized recommendations** based on activity type
- **Risk level scoring** from low to very high

### 📊 Comprehensive Weather Analysis
- **Multi-parameter prediction**: Temperature, rainfall, wind, comfort index
- **Historical data training**: 70+ years of weather data
- **Probability-based output**: Not just yes/no, but likelihood percentages

### ⚡ Production-Ready API
- **RESTful endpoints** for easy integration
- **JSON responses** with detailed risk breakdowns
- **Error handling** and validation
- **CORS enabled** for frontend integration

## 🎯 Next Development Phase

### Phase 1: Frontend Development
- [ ] Tauri desktop application
- [ ] React Native mobile apps
- [ ] Marketing website with animations

### Phase 2: Enhanced Intelligence  
- [ ] Real-time weather API integration (NASA/NOAA)
- [ ] Location-based geocoding services
- [ ] Historical accuracy tracking
- [ ] User preference learning

### Phase 3: Production Features
- [ ] User accounts and history
- [ ] Push notifications for weather changes
- [ ] Social sharing and trip planning
- [ ] Enterprise/B2B features

## 🏆 Hackathon Demo Points

1. **Problem Solving**: Addresses real outdoor planning challenges
2. **AI/ML Integration**: Custom models for weather classification
3. **Activity Intelligence**: Goes beyond generic weather apps
4. **Earth Science**: Uses historical climate data analysis
5. **Multi-Platform Vision**: Desktop, mobile, and web applications
6. **Production Quality**: Professional API design and documentation

## 📈 Performance Metrics
- **Model Accuracy**: 95%+ on test data
- **API Response Time**: ~2 seconds average
- **Data Coverage**: 25,500+ historical weather records
- **Activity Support**: 5 major outdoor activity categories

## 🌍 Vision Statement
*"Empower people to make confident outdoor decisions by providing AI-powered, activity-specific weather risk assessments that go beyond traditional forecasts."*

---

**Status**: Python Backend Complete ✅ | Ready for Frontend Development 🚀