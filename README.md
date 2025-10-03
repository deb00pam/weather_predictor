# NASA Weather Risk Detection API

A personalized weather risk assessment tool for outdoor activities using NASA POWER Earth observation data.

## 🌟 Features

- **Location Search**: Convert place names to coordinates using OpenStreetMap
- **Historical Weather Analysis**: Access 10+ years of NASA POWER meteorological data
- **Risk Assessment**: Calculate probabilities for adverse weather conditions:
  - Very Hot (>35°C)
  - Very Cold (<0°C) 
  - Very Windy (>15 m/s)
  - Very Wet (>25mm rain)
  - Very Uncomfortable (Heat Index >40°C)
- **Activity-Specific Recommendations**: Tailored advice for hiking, camping, fishing
- **Confidence Scoring**: Data quality assessment based on historical sample size

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Internet connection for NASA POWER and OpenStreetMap APIs

### Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python start_server.py
   ```

4. **Access the API:**
   - Server: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

### Testing

Run the test suite to verify everything works:
```bash
python test_api.py
```

## 📖 API Endpoints

### POST /api/geocode
Convert location name to coordinates
```json
{
  "location_name": "New York City"
}
```

### POST /api/weather-risk
Analyze weather risk for location and dates
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "start_date": "2024-07-15",
  "end_date": "2024-07-20",
  "activity_type": "hiking"
}
```

## 🛠️ Project Structure

```
weather/
├── main.py                     # FastAPI application
├── requirements.txt            # Python dependencies
├── start_server.py            # Server startup script
├── test_api.py               # API test suite
├── services/
│   ├── nasa_power_client.py  # NASA POWER API client
│   ├── location_service.py   # OpenStreetMap geocoding
│   └── weather_risk_analyzer.py # Risk calculation engine
└── README.md
```

## 🌍 Data Sources

- **NASA POWER**: Historical meteorological data from satellite observations
- **OpenStreetMap Nominatim**: Free geocoding service for location conversion

## 🎯 Use Cases

Perfect for planning:
- 🥾 Hiking trips
- ⛺ Camping adventures  
- 🎣 Fishing expeditions
- 🏃‍♀️ Outdoor sports events
- 🎪 Festivals and gatherings

## 📊 Risk Analysis

The system analyzes historical weather patterns to calculate:
- **Probability percentages** for each adverse condition
- **Confidence scores** based on data availability
- **Activity-specific risk adjustments**
- **Personalized recommendations** for safety

## 🔧 Configuration

### Weather Risk Thresholds
- Very Hot: >35°C (95°F)
- Very Cold: <0°C (32°F)
- Very Windy: >15 m/s (33 mph)
- Very Wet: >25mm (1 inch) rain
- Very Uncomfortable: Heat Index >40°C (104°F)

### Activity Risk Multipliers
Different activities have varying sensitivity to weather conditions:
- **Hiking**: Higher risk for temperature extremes
- **Camping**: Very sensitive to wind and cold
- **Fishing**: Moderate sensitivity to wind
- **General**: Baseline risk assessment

## 🤝 Contributing

This project was developed for the NASA Space Apps Challenge. Contributions welcome!

## 📄 License

Open source - built for the NASA Space Apps hackathon.

## 🙏 Acknowledgments

- NASA POWER team for providing free access to Earth observation data
- OpenStreetMap contributors for location data
- NASA Space Apps Challenge for the inspiration