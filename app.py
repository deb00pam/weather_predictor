from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import traceback
from datetime import datetime

from config import Config
from services.location import LocationService
from services.nasa_power import NASAPowerService
from services.gemini import GeminiService

app = Flask(__name__)
CORS(app)

# Initialize services
try:
    Config.validate_config()
    location_service = LocationService()
    weather_service = NASAPowerService()
    gemini_service = GeminiService()
    print("✅ All services initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing services: {e}")
    location_service = weather_service = gemini_service = None

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and return weather analysis"""
    try:
        # Get user message
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Please provide a message'
            })
        
        # Check if services are available
        if not all([location_service, weather_service, gemini_service]):
            return jsonify({
                'success': False,
                'error': 'Weather services are currently unavailable. Please check your API configuration.'
            })
        
        # Process the user's request
        response = process_weather_request(user_message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Sorry, I encountered an error processing your request. Please try again.'
        })

def process_weather_request(user_message: str) -> str:
    """Process a weather request and return analysis"""
    try:
        # Step 1: Extract location from user message
        location_name = location_service.extract_location_from_text(user_message)
        
        if not location_name:
            return """I'd be happy to help with weather analysis! However, I need to know which location you're interested in. 
            
Please try asking something like:
- "What's the weather like for hiking in Colorado?"
- "Is it good for camping in Yellowstone?"
- "Show me weather patterns for fishing in Lake Tahoe"

Just mention the place you want to visit and I'll analyze the weather data for you!"""
        
        # Step 2: Get coordinates for the location
        coordinates = location_service.get_coordinates(location_name)
        if not coordinates:
            return f"Sorry, I couldn't find the location '{location_name}'. Could you try being more specific? For example, include the state or country name."
        
        latitude, longitude = coordinates
        
        # Step 3: Get detailed location information
        location_info = location_service.get_location_info(location_name)
        if not location_info:
            location_info = {
                'name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'full_address': location_name
            }
        
        # Step 4: Fetch weather data from NASA POWER
        # Get recent historical data (last 30 days) for current patterns
        weather_data = weather_service.get_historical_data(latitude, longitude, days_back=30)
        
        if not weather_data:
            return f"Sorry, I couldn't retrieve weather data for {location_name}. This might be due to the location being over water or API limitations. Please try a different location."
        
        # Step 5: Analyze the weather data
        weather_analysis = weather_service.analyze_weather_conditions(weather_data)
        
        # Step 6: Get AI analysis and recommendations from Gemini
        ai_response = gemini_service.analyze_weather_for_activities(
            location_info, weather_data, weather_analysis, user_message
        )
        
        return ai_response
        
    except Exception as e:
        print(f"Error processing weather request: {e}")
        traceback.print_exc()
        return "Sorry, I encountered an error while analyzing the weather data. Please try again with a different location or rephrase your question."

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        Config.validate_config()
        return jsonify({
            'status': 'healthy',
            'services': {
                'location': location_service is not None,
                'weather': weather_service is not None,
                'gemini': gemini_service is not None
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🌤️ Starting Weather Predictor Chatbot...")
    print("📍 Make sure you have:")
    print("   1. Created a .env file with your GEMINI_API_KEY")
    print("   2. Installed requirements: pip install -r requirements.txt")
    print("🚀 Starting server on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)