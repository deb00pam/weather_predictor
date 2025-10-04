#!/usr/bin/env python3
"""
Quick test script to verify all components are working
Run this before starting the main application
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading"""
    try:
        from config import Config
        Config.validate_config()
        print("✅ Configuration: OK")
        return True
    except Exception as e:
        print(f"❌ Configuration: {e}")
        return False

def test_location_service():
    """Test location service"""
    try:
        from services.location import LocationService
        service = LocationService()
        
        # Test location extraction
        location = service.extract_location_from_text("hiking in Colorado")
        if location:
            print(f"✅ Location Service: Extracted '{location}' from text")
        else:
            print("⚠️ Location Service: Could not extract location")
        
        # Test geocoding
        coords = service.get_coordinates("New York")
        if coords:
            print(f"✅ Location Service: Geocoding OK ({coords[0]:.2f}, {coords[1]:.2f})")
            return True
        else:
            print("❌ Location Service: Geocoding failed")
            return False
    except Exception as e:
        print(f"❌ Location Service: {e}")
        return False

def test_weather_service():
    """Test NASA POWER service"""
    try:
        from services.nasa_power import NASAPowerService
        service = NASAPowerService()
        
        # Test with New York coordinates
        weather_data = service.get_historical_data(40.7128, -74.0060, days_back=7)
        if weather_data and weather_data.get('temperature'):
            print(f"✅ Weather Service: Retrieved {len(weather_data['temperature'])} days of data")
            
            # Test analysis
            analysis = service.analyze_weather_conditions(weather_data)
            if analysis:
                print(f"✅ Weather Analysis: {analysis['total_days']} days analyzed")
                return True
        
        print("❌ Weather Service: No data retrieved")
        return False
    except Exception as e:
        print(f"❌ Weather Service: {e}")
        return False

def test_gemini_service():
    """Test Gemini AI service"""
    try:
        from services.gemini import GeminiService
        service = GeminiService()
        
        # Simple test
        location_info = {'name': 'Test Location', 'full_address': 'Test, USA'}
        weather_analysis = {'total_days': 7, 'avg_temperature': 20}
        
        response = service._create_fallback_response(weather_analysis, location_info)
        if response and len(response) > 50:
            print("✅ Gemini Service: Fallback response OK")
            return True
        else:
            print("❌ Gemini Service: Response too short")
            return False
    except Exception as e:
        print(f"❌ Gemini Service: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Weather Predictor Chatbot Components\n")
    
    tests = [
        ("Configuration", test_config),
        ("Location Service", test_location_service),
        ("Weather Service", test_weather_service),
        ("Gemini AI Service", test_gemini_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your chatbot is ready to run.")
        print("💡 Next steps:")
        print("   1. Make sure your .env file has a valid GEMINI_API_KEY")
        print("   2. Run: python app.py")
        print("   3. Open: http://localhost:5000")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        print("💡 Common issues:")
        print("   - Missing or invalid GEMINI_API_KEY in .env file")
        print("   - Network connectivity issues")
        print("   - Missing dependencies (run: pip install -r requirements.txt)")

if __name__ == "__main__":
    main()