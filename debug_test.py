import requests
import json

def debug_weather_risk():
    print("🔍 Debug Weather Risk Analysis")
    
    # Test with Paris coordinates
    response = requests.post(
        "http://localhost:8000/api/weather-risk",
        json={
            "latitude": 48.8566,
            "longitude": 2.3522,
            "start_date": "2024-07-15",
            "end_date": "2024-07-20",
            "activity_type": "hiking"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"Risk categories count: {len(data.get('risk_categories', []))}")
        
        for i, category in enumerate(data.get("risk_categories", [])):
            print(f"\nCategory {i+1}:")
            for key, value in category.items():
                print(f"  {key}: {value}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    debug_weather_risk()