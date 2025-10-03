import requests
import json

def test_api():
    print("NASA Weather Risk Detection API - Quick Test")
    print("=" * 50)
    
    # Test health check
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json()["status"])
        else:
            print("❌ Health check failed:", response.status_code)
            return
    except Exception as e:
        print("❌ Server not running:", e)
        return
    
    # Test geocoding
    try:
        response = requests.post(
            "http://localhost:8000/api/geocode",
            json={"location_name": "Paris, France"}
        )
        if response.status_code == 200:
            data = response.json()
            if data:
                location = data[0]
                print(f"✅ Geocoding works: {location['name']} ({location['latitude']:.2f}, {location['longitude']:.2f})")
                
                # Test weather risk with this location
                risk_response = requests.post(
                    "http://localhost:8000/api/weather-risk",
                    json={
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                        "start_date": "2024-07-15",
                        "end_date": "2024-07-20",
                        "activity_type": "hiking"
                    }
                )
                
                if risk_response.status_code == 200:
                    risk_data = risk_response.json()
                    print(f"✅ Weather risk analysis works!")
                    print(f"   Overall Risk Score: {risk_data['overall_risk_score']}%")
                    print(f"   Historical Data Years: {risk_data['historical_data_years']}")
                else:
                    print(f"❌ Weather risk analysis failed: {risk_response.status_code}")
                    print(f"   Error: {risk_response.text}")
            else:
                print("❌ No geocoding results")
        else:
            print(f"❌ Geocoding failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    print("\n✅ Quick test completed!")
    print("🌐 Full API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()