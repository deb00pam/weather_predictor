"""
Test script for WeatherWise API
Run this after starting the API server to test functionality
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test the WeatherWise API endpoints"""
    
    print("🌤️  Testing WeatherWise API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Get activities
    print("\n2. Testing activities endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/activities")
        activities = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Available activities: {list(activities['activities'].keys())}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Simple weather prediction
    print("\n3. Testing simple weather prediction...")
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        params = {
            "date_str": tomorrow,
            "lat": 40.7128,  # New York
            "lon": -74.0060,
            "activity": "hiking"
        }
        response = requests.get(f"{BASE_URL}/predict-weather-simple", params=params)
        result = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Date: {result.get('date')}")
        print(f"   Activity: {result.get('activity')}")
        print(f"   Overall Risk: {result.get('prediction', {}).get('risk_level')}")
        print(f"   Risk Score: {result.get('prediction', {}).get('overall_risk_score', 0):.2f}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Detailed weather prediction (POST)
    print("\n4. Testing detailed weather prediction...")
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        payload = {
            "date": tomorrow,
            "location": {
                "latitude": 37.7749,  # San Francisco
                "longitude": -122.4194,
                "location_name": "San Francisco, CA"
            },
            "activity": "camping"
        }
        response = requests.post(f"{BASE_URL}/predict-weather", json=payload)
        result = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Location: {result.get('location', {}).get('location_name')}")
        print(f"   Activity: {result.get('activity')}")
        
        prediction = result.get('prediction', {})
        print(f"   Overall Risk: {prediction.get('risk_level')} ({prediction.get('overall_risk_score', 0):.2f})")
        
        conditions = prediction.get('conditions', {})
        print("   Individual Conditions:")
        for condition, data in conditions.items():
            prob = data.get('probability', 0)
            risk = data.get('risk_level', 'unknown')
            print(f"     {condition.replace('_', ' ').title()}: {prob:.2f} ({risk})")
        
        recommendations = prediction.get('recommendations', [])
        if recommendations:
            print("   Recommendations:")
            for rec in recommendations:
                print(f"     • {rec}")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API testing complete!")
    print("\nTo start the API server, run:")
    print("   python api_server.py")

if __name__ == "__main__":
    test_api()