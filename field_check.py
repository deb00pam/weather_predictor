import requests
import json

def check_missing_fields():
    print("🔍 Checking for missing fields in weather risk response")
    
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
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response successful")
        
        required_fields = ["category", "probability", "threshold_value", "risk_level", "description", "activity_impact", "confidence", "sample_size", "historical_events"]
        
        for i, category in enumerate(data.get("risk_categories", [])):
            print(f"\nCategory {i+1} ({category.get('category', 'unknown')}):")
            
            missing_fields = []
            for field in required_fields:
                if field in category:
                    print(f"  ✅ {field}: {category[field]}")
                else:
                    missing_fields.append(field)
                    print(f"  ❌ MISSING: {field}")
            
            if missing_fields:
                print(f"  🚨 Missing fields: {missing_fields}")
            else:
                print(f"  ✅ All fields present")
    else:
        print(f"❌ API Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    check_missing_fields()