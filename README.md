# 🌦️ NASA Weather Risk Detection App

> **🏆 NASA Space Apps Challenge 2025 Project**

A comprehensive weather risk assessment application featuring a Python FastAPI backend and Electron desktop interface, designed to help users make informed decisions about outdoor activities using NASA POWER Earth observation data.

## 🌟 Features

### 🎯 **Core Functionality**
- **🌍 Global Location Search**: Convert place names to coordinates using OpenStreetMap
- **📊 Historical Weather Analysis**: Access 10+ years of NASA POWER meteorological data
- **⚠️ Advanced Risk Assessment**: Calculate probabilities for 5 adverse weather conditions
- **🎯 Activity-Specific Analysis**: Tailored recommendations for different outdoor activities
- **📈 Data Visualization**: Interactive charts and graphs (optional/expandable)
- **💯 Confidence Scoring**: Data quality assessment based on historical sample size

### 🖥️ **Desktop Application**
- **Modern Electron Interface**: Cross-platform desktop application
- **Intuitive UI**: NASA-themed design with responsive layout
- **Real-time Analysis**: Live connection to weather risk API
- **Optional Charts**: Expandable data visualizations to prevent scrolling issues
- **Professional Design**: Clean, modern interface optimized for user experience

### ⚡ **Weather Risk Categories**
- 🔥 **Very Hot**: >35°C (95°F)
- 🧊 **Very Cold**: <0°C (32°F) 
- 💨 **Very Windy**: >15 m/s (33 mph)
- 🌧️ **Very Wet**: >25mm (1 inch) rain
- 🥵 **Very Uncomfortable**: Heat Index >40°C (104°F)

## 🚀 Quick Start

### 📋 Prerequisites
- **Python 3.8+** for backend
- **Node.js 16+** for desktop app
- **Internet connection** for NASA POWER and OpenStreetMap APIs

### 🔧 Installation & Setup

#### 1. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python start_server.py
```

#### 2. **Desktop App Setup**
```bash
# Navigate to desktop app directory
cd desktop-app

# Install Node.js dependencies
npm install

# Launch the desktop application
npm start
```

#### 3. **Access Points**
- **🖥️ Desktop App**: Launches automatically with `npm start`
- **🌐 API Server**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/api/health

### 🧪 Testing

Verify everything works with the comprehensive test suite:
```bash
python test_api.py
```

## 📖 API Endpoints

### `POST /api/geocode`
Convert location name to coordinates
```json
{
  "location_name": "New York City"
}
```

**Response:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "display_name": "New York City, NY, USA"
}
```

### `POST /api/weather-risk`
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

**Response:**
```json
{
  "overall_risk_score": 15.2,
  "risk_level": "Low",
  "location": "New York City, NY, USA",
  "risk_categories": [...],
  "recommendations": [...],
  "data_years": 14
}
```

### `GET /api/health`
Check API server status
```json
{
  "status": "healthy",
  "message": "NASA Weather Risk Detection API is running"
}
```

## 🏗️ Project Structure

```
weather/
├── 📁 desktop-app/                 # Electron Desktop Application
│   ├── 📄 package.json           # Node.js dependencies & scripts
│   ├── 📄 main.js                # Electron main process
│   ├── 📄 index.html             # Application UI
│   ├── 📁 styles/
│   │   └── 📄 main.css           # NASA-themed styling
│   └── 📁 js/
│       ├── 📄 api.js             # Backend API integration
│       ├── 📄 ui.js              # User interface management
│       ├── 📄 charts.js          # Data visualization
│       └── 📄 app.js             # Application controller
├── 📁 services/                   # Backend Services
│   ├── 📄 nasa_power_client.py   # NASA POWER API integration
│   ├── 📄 location_service.py    # OpenStreetMap geocoding
│   └── 📄 weather_risk_analyzer.py # Risk calculation engine
├── 📄 main.py                     # FastAPI application server
├── 📄 requirements.txt            # Python dependencies
├── 📄 start_server.py            # Server startup script
├── 📄 test_api.py                # Comprehensive API tests
├── 📄 .gitignore                 # Git ignore rules
└── 📄 README.md                  # This documentation
```

## 🌍 Data Sources & Technology

### 🛰️ **NASA POWER (Prediction of Worldwide Energy Resources)**
- **Historical meteorological data** from satellite and model-based observations
- **Global coverage** with 0.5° x 0.625° spatial resolution
- **14+ years** of reliable weather data for accurate risk assessment
- **Multiple parameters**: Temperature, wind speed, precipitation, humidity

### 🗺️ **OpenStreetMap Nominatim**
- **Free geocoding service** for global location conversion
- **Community-driven** location database
- **No API key required** for basic usage
- **High accuracy** for major cities and landmarks

### 💻 **Technology Stack**
- **Backend**: Python FastAPI for high-performance API
- **Frontend**: Electron for cross-platform desktop application
- **Data Processing**: Pandas & NumPy for efficient data analysis
- **Visualization**: Chart.js for interactive charts and graphs
- **HTTP Client**: Axios for reliable API communication

## 🎯 Use Cases & Applications

### 🏞️ **Outdoor Recreation**
- 🥾 **Hiking & Trekking**: Temperature and wind risk assessment
- ⛺ **Camping**: Cold weather and precipitation warnings
- 🎣 **Fishing**: Wind and weather comfort analysis
- 🏃‍♀️ **Running & Sports**: Heat index and safety recommendations

### 🎪 **Event Planning**
- � **Outdoor Festivals**: Weather risk for large gatherings
- 🏫 **School Activities**: Safety planning for outdoor events
- 💼 **Corporate Events**: Professional outdoor activity planning
- � **Weddings & Parties**: Weather contingency planning

### 🚁 **Professional Applications**
- 🚧 **Construction Planning**: Weather-dependent project scheduling
- 🚁 **Aviation Support**: Supplementary weather risk information
- 🌾 **Agriculture**: Planting and harvesting condition analysis
- 📋 **Emergency Planning**: Risk assessment for disaster response

## 📊 Risk Analysis Methodology

### 🧮 **Statistical Analysis**
- **Historical Percentile Calculation**: Analyzes 14+ years of daily weather data
- **Probability Assessment**: Calculates likelihood of adverse conditions
- **Confidence Scoring**: Based on data sample size and variability
- **Activity Adjustments**: Risk multipliers based on activity sensitivity

### 🎯 **Risk Categories & Thresholds**
| Risk Type | Threshold | Impact |
|-----------|-----------|---------|
| 🔥 Very Hot | >35°C (95°F) | Heat exhaustion, dehydration |
| 🧊 Very Cold | <0°C (32°F) | Hypothermia, frostbite risk |
| 💨 Very Windy | >15 m/s (33 mph) | Equipment damage, safety hazards |
| 🌧️ Very Wet | >25mm (1 inch) | Flooding, equipment damage |
| 🥵 Very Uncomfortable | Heat Index >40°C | Extreme heat stress |

### 🎛️ **Activity-Specific Risk Multipliers**
- **🥾 Hiking**: 1.3x temperature sensitivity (exposure risk)
- **⛺ Camping**: 1.5x cold & wind sensitivity (shelter limitations)
- **🎣 Fishing**: 1.2x wind sensitivity (water safety)
- **🏃‍♀️ General**: 1.0x baseline risk assessment

## 🖥️ Desktop Application Features

### 🎨 **User Interface**
- **NASA-Inspired Design**: Professional space agency aesthetic
- **Responsive Layout**: Works on different screen sizes
- **Intuitive Navigation**: Easy-to-use form-based interface
- **Real-time Feedback**: Instant API status and error handling

### 📈 **Data Visualization**
- **Optional Charts**: Toggle-able data visualizations
- **Risk Probability Charts**: Bar charts showing risk percentages
- **Overall Risk Gauge**: Visual risk score indicator
- **No Scroll Issues**: Charts are expandable to prevent UI problems

### ⚡ **Performance Features**
- **Fast Loading**: Optimized API calls and caching
- **Error Handling**: Graceful degradation with user feedback
- **Memory Management**: Charts created/destroyed on demand
- **Background Processing**: Non-blocking API requests

## 🔧 Configuration & Customization

### 🌡️ **Weather Risk Thresholds**
```python
RISK_THRESHOLDS = {
    "very_hot": 35.0,        # Celsius
    "very_cold": 0.0,        # Celsius  
    "very_windy": 15.0,      # m/s
    "very_wet": 25.0,        # mm/day
    "heat_index_limit": 40.0  # Celsius
}
```

### 🎯 **Activity Risk Multipliers**
```python
ACTIVITY_MULTIPLIERS = {
    "hiking": {"temp": 1.3, "wind": 1.1},
    "camping": {"cold": 1.5, "wind": 1.4},
    "fishing": {"wind": 1.2},
    "general": {"all": 1.0}
}
```

### 🔌 **API Configuration**
- **NASA POWER**: No API key required (free tier)
- **OpenStreetMap**: Rate-limited (1 request/second)
- **CORS**: Enabled for desktop app integration
- **Timeout**: 30 seconds for external API calls

## 🚀 Development & Deployment

### 🛠️ **Development Setup**
```bash
# Clone the repository
git clone https://github.com/deb00pam/weather_predictor.git
cd weather_predictor

# Backend development
pip install -r requirements.txt
python start_server.py

# Frontend development
cd desktop-app
npm install
npm start
```

### 📦 **Building for Distribution**
```bash
# Build Electron app for distribution
cd desktop-app
npm run build

# Package for different platforms
npm run dist
```

### 🧪 **Testing**
```bash
# Run API tests
python test_api.py

# Test individual components
python -m pytest services/

# Frontend testing
cd desktop-app
npm test
```

## 🤝 Contributing

This project was developed for the **NASA Space Apps Challenge 2025**. 

### 🌟 **Contributors Welcome**
- 🐛 Bug reports and fixes
- ✨ Feature enhancements
- 📖 Documentation improvements
- 🎨 UI/UX improvements
- 🧪 Additional test coverage

### 📝 **Development Guidelines**
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Include tests for new features
- Update documentation for changes

## 📄 License

**MIT License** - Open source project built for the NASA Space Apps hackathon.

## 🙏 Acknowledgments

- 🛰️ **NASA POWER Team** for providing free access to Earth observation data
- 🌍 **OpenStreetMap Contributors** for global location data
- 🚀 **NASA Space Apps Challenge** for the inspiration and platform
- 👥 **Open Source Community** for the amazing tools and libraries

## 📞 Support & Contact

- 🐛 **Issues**: Report bugs via GitHub Issues
- 💡 **Feature Requests**: Suggest improvements via GitHub Discussions
- 📧 **Contact**: Built for NASA Space Apps Challenge 2025

---

### 🏆 **NASA Space Apps Challenge 2025**
*Building solutions for a better tomorrow using Earth observation data*