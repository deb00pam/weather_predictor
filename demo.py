"""
WeatherWise Demo Script
Demonstrates the weather prediction API capabilities
"""

import requests
import json
from datetime import datetime, timedelta
import time

# API base URL
BASE_URL = "http://localhost:8000"

def print_banner():
    print("🌤️" + "=" * 60 + "🌤️")
    print("           WEATHERWISE - INTELLIGENT WEATHER PREDICTION")
    print("              Activity-Specific Weather Risk Assessment")
    print("🌤️" + "=" * 60 + "🌤️")

def test_different_activities():
    """Demo weather predictions for different activities"""
    print("\n🎯 ACTIVITY-SPECIFIC WEATHER RISK ASSESSMENT")
    print("-" * 50)
    
    # Test different locations and activities
    test_cases = [
        {
            "location": {"lat": 40.7128, "lon": -74.0060, "name": "New York City"},
            "activity": "hiking",
            "date": "2024-10-15"
        },
        {
            "location": {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"},
            "activity": "fishing", 
            "date": "2024-10-20"
        },
        {
            "location": {"lat": 25.7617, "lon": -80.1918, "name": "Miami"},
            "activity": "beach_vacation",
            "date": "2024-11-01"
        },
        {
            "location": {"lat": 39.7392, "lon": -104.9903, "name": "Denver"},
            "activity": "camping",
            "date": "2024-10-25"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['location']['name']} - {case['activity'].replace('_', ' ').title()}")
        print(f"   Date: {case['date']}")
        
        try:
            params = {
                "date_str": case['date'],
                "lat": case['location']['lat'],
                "lon": case['location']['lon'],
                "activity": case['activity']
            }
            
            response = requests.get(f"{BASE_URL}/predict-weather-simple", params=params)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result['prediction']
                
                # Overall risk
                risk_color = {
                    'low': '🟢', 'medium': '🟡', 'high': '🟠', 'very_high': '🔴'
                }.get(prediction['risk_level'], '⚪')
                
                print(f"   Overall Risk: {risk_color} {prediction['risk_level'].upper()} ({prediction['overall_risk_score']:.2f})")
                
                # Individual conditions
                conditions = prediction['conditions']
                print("   Specific Conditions:")
                for condition, data in conditions.items():
                    prob = data['probability']
                    level = data['risk_level']
                    icon = '🟢' if prob < 0.3 else '🟡' if prob < 0.6 else '🔴'
                    print(f"     {icon} {condition.replace('_', ' ').title()}: {prob:.2f} ({level})")
                
                # Recommendations
                if prediction['recommendations']:
                    print("   💡 Recommendations:")
                    for rec in prediction['recommendations']:
                        print(f"     • {rec}")
                        
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay for better UX

def show_available_activities():
    """Show all available activity types"""
    print("\n📋 AVAILABLE ACTIVITY TYPES")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/activities")
        if response.status_code == 200:
            activities = response.json()['activities']
            for key, name in activities.items():
                print(f"   • {name} ({key})")
        else:
            print("   ❌ Could not fetch activities")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_api_performance():
    """Test API response times"""
    print("\n⚡ API PERFORMANCE TEST")
    print("-" * 25)
    
    test_endpoint = f"{BASE_URL}/predict-weather-simple"
    params = {
        "date_str": "2024-10-15",
        "lat": 40.7128,
        "lon": -74.0060,
        "activity": "hiking"
    }
    
    times = []
    for i in range(5):
        start = time.time()
        try:
            response = requests.get(test_endpoint, params=params)
            end = time.time()
            if response.status_code == 200:
                times.append(end - start)
                print(f"   Request {i+1}: {(end-start)*1000:.1f}ms ✅")
            else:
                print(f"   Request {i+1}: Failed ❌")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n   Average response time: {avg_time*1000:.1f}ms")

def demonstrate_risk_levels():
    """Show how risk levels change with different conditions"""
    print("\n🌡️ WEATHER CONDITION DEMONSTRATION")
    print("-" * 35)
    print("This shows how the same location can have different risks for different activities:")
    
    activities = ['hiking', 'fishing', 'camping', 'outdoor_sports', 'beach_vacation']
    
    for activity in activities:
        try:
            params = {
                "date_str": "2024-07-15",  # Summer date
                "lat": 33.4484,  # Los Angeles
                "lon": -118.2437,
                "activity": activity
            }
            
            response = requests.get(f"{BASE_URL}/predict-weather-simple", params=params)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result['prediction']
                
                risk_icon = {
                    'low': '🟢', 'medium': '🟡', 'high': '🟠', 'very_high': '🔴'
                }.get(prediction['risk_level'], '⚪')
                
                print(f"   {activity.replace('_', ' ').title():15} {risk_icon} {prediction['risk_level']:10} ({prediction['overall_risk_score']:.2f})")
                
        except Exception as e:
            print(f"   {activity:15} ❌ Error")

def main():
    """Main demo function"""
    print_banner()
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not running. Please start the server with: python api_server.py")
            return
    except Exception:
        print("❌ Cannot connect to API. Please ensure the server is running on http://localhost:8000")
        print("   Start with: python api_server.py")
        return
    
    print("✅ Connected to WeatherWise API")
    
    # Run demos
    show_available_activities()
    test_different_activities()
    demonstrate_risk_levels()
    test_api_performance()
    
    print("\n" + "🌤️" + "=" * 60 + "🌤️")
    print("                    DEMO COMPLETE!")
    print("🌤️" + "=" * 60 + "🌤️")
    
    print("\n📚 Next Steps:")
    print("   • Check out the interactive API docs: http://localhost:8000/docs")
    print("   • Build frontend applications using these endpoints")
    print("   • Integrate with real-time weather APIs for production")

if __name__ == "__main__":
    main()