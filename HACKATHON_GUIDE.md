# Weather Predictor Chatbot - Hackathon Setup Guide

## Quick Start (5 minutes!)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Gemini API Key
1. Copy `.env.template` to `.env`
2. Add your Gemini API key to `.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Test the Setup
```bash
python test_components.py
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open Browser
Navigate to: `http://localhost:5000`

---

## 🎯 Hackathon Demo Features

### Core Functionality
- **Natural Language Processing**: Ask questions in plain English
- **NASA POWER Data**: Real weather data from satellites
- **AI Analysis**: Google Gemini analyzes patterns and gives recommendations
- **Location Intelligence**: Supports any location worldwide
- **Activity Recommendations**: Suggests outdoor activities based on weather

### Demo Questions to Try
```
"What's the weather like for hiking in Colorado?"
"Is it good for camping in Yellowstone this weekend?"
"Show me weather patterns for fishing in Florida"
"Can I go skiing in the Alps next month?"
```

### Technical Highlights
- **Multi-API Integration**: NASA POWER + Google Gemini + OpenStreetMap
- **Real-time Analysis**: Fetches current weather data and historical patterns
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Graceful fallbacks for API failures
- **Scalable Architecture**: Modular services for easy expansion

---

## 🏗️ Architecture Overview

```
User Input → Location Extraction → NASA POWER API → Gemini AI → Response
     ↓              ↓                    ↓             ↓         ↓
   Chat UI    OpenStreetMap      Weather Data    AI Analysis  Recommendations
```

### Key Components
- **Flask Backend**: REST API with chat endpoint
- **Location Service**: Geocoding and location extraction
- **NASA POWER Service**: Weather data fetching and analysis
- **Gemini Service**: AI-powered recommendations
- **React-like Frontend**: Modern chat interface

---

## 📊 Data Sources

### NASA POWER API
- **Temperature**: 2-meter air temperature
- **Precipitation**: Corrected precipitation data
- **Wind Speed**: 2-meter wind speed
- **Humidity**: Relative humidity at 2 meters
- **Pressure**: Surface pressure
- **Coverage**: Global, satellite-based

### Weather Classifications
- **Very Hot**: >35°C (95°F)
- **Very Cold**: <0°C (32°F)
- **Very Windy**: >15 m/s (33 mph)
- **Very Wet**: >10mm/day precipitation
- **Very Uncomfortable**: High temp + humidity or extreme conditions

---

## 🎪 Presentation Tips

### Problem Statement
"Planning outdoor activities is risky without knowing weather patterns. Our solution helps users make informed decisions about outdoor events by analyzing real satellite data."

### Solution Highlights
1. **Conversational Interface**: No complex forms or menus
2. **Real Data**: NASA satellite observations, not just forecasts
3. **Smart Recommendations**: AI considers location-specific activities
4. **Historical Patterns**: Shows trends, not just current conditions
5. **Global Coverage**: Works anywhere in the world

### Demo Flow
1. Show the clean, modern interface
2. Ask about a popular location (e.g., "hiking in Yellowstone")
3. Highlight the AI analysis and recommendations
4. Try different activities and locations
5. Show mobile responsiveness

### Technical Achievements
- **3 Major APIs** integrated seamlessly
- **Real-time processing** of satellite data
- **AI-powered insights** with contextual recommendations
- **Responsive design** for any device
- **Production-ready** error handling

---

## 🚀 Future Enhancements

- **User Accounts**: Save favorite locations and activities
- **Weather Alerts**: Notifications for optimal conditions
- **Social Features**: Share recommendations with friends
- **Mobile App**: Native iOS/Android applications
- **Machine Learning**: Improve predictions with usage data

---

## 🛠️ Troubleshooting

### Common Issues
1. **No Gemini API Key**: Copy `.env.template` to `.env` and add your key
2. **Location Not Found**: Try being more specific (include state/country)
3. **No Weather Data**: Some oceanic locations may not have data
4. **Slow Response**: First request may take longer due to API warm-up

### Debug Mode
The app runs in debug mode by default. Check console output for detailed error messages.

---

## 📝 Credits
- **Weather Data**: NASA POWER API
- **AI Analysis**: Google Gemini
- **Location Services**: OpenStreetMap/Nominatim
- **Frontend**: Custom HTML/CSS/JS
- **Backend**: Python Flask