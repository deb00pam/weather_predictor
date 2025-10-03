"""
Test script for NASA Weather Risk Detection API
Tests all major functionality and endpoints
"""

import asyncio
import httpx
import json
from datetime import date, datetime

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing health check endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_geocoding(self):
        """Test the geocoding endpoint"""
        print("\n🌍 Testing geocoding endpoint...")
        test_locations = [
            "New York City",
            "London, UK", 
            "Tokyo, Japan",
            "Sydney, Australia"
        ]
        
        results = []
        for location in test_locations:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/geocode",
                    json={"location_name": location}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        result = data[0]  # Take the first result
                        print(f"✅ {location}: {result['name']} ({result['latitude']:.2f}, {result['longitude']:.2f})")
                        results.append(result)
                    else:
                        print(f"❌ {location}: No results found")
                else:
                    print(f"❌ {location}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {location}: Exception {e}")
        
        return results
    
    async def test_weather_risk_analysis(self, locations):
        """Test weather risk analysis endpoint"""
        print("\n⛈️ Testing weather risk analysis...")
        
        if not locations:
            print("❌ No locations to test")
            return False
        
        # Test with the first location
        location = locations[0]
        test_dates = [
            (date(2024, 6, 15), date(2024, 6, 20)),   # Summer
            (date(2024, 12, 20), date(2024, 12, 25)), # Winter
            (date(2024, 3, 15), date(2024, 3, 20))    # Spring
        ]
        
        for start_date, end_date in test_dates:
            try:
                print(f"\n📅 Testing {start_date} to {end_date} at {location['name']}")
                
                response = await self.client.post(
                    f"{self.base_url}/api/weather-risk",
                    json={
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "activity_type": "hiking"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Analysis completed:")
                    print(f"   Overall Risk Score: {data['overall_risk_score']}%")
                    print(f"   Historical Data Years: {data['historical_data_years']}")
                    
                    # Display risk categories
                    for category in data["risk_categories"]:
                        risk_level = category["risk_level"]
                        probability = category["probability"]
                        description = category["description"]
                        print(f"   {description}: {probability}% ({risk_level})")
                    
                    # Show recommendations
                    print(f"   Recommendations:")
                    for rec in data["recommendations"][:3]:  # Show first 3
                        print(f"     • {rec}")
                    
                    return True
                else:
                    print(f"❌ Weather analysis failed: {response.status_code}")
                    if response.content:
                        print(f"   Error: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Weather analysis exception: {e}")
                return False
    
    async def test_invalid_requests(self):
        """Test error handling with invalid requests"""
        print("\n🚫 Testing error handling...")
        
        # Test invalid geocoding
        try:
            response = await self.client.post(
                f"{self.base_url}/api/geocode",
                json={"location_name": ""}
            )
            if response.status_code == 404:
                print("✅ Empty location properly rejected")
            else:
                print(f"❌ Empty location should return 404, got {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing invalid geocoding: {e}")
        
        # Test invalid coordinates
        try:
            response = await self.client.post(
                f"{self.base_url}/api/weather-risk",
                json={
                    "latitude": 999.0,  # Invalid latitude
                    "longitude": 0.0,
                    "start_date": date.today().isoformat(),
                    "end_date": date.today().isoformat(),
                    "activity_type": "hiking"
                }
            )
            if response.status_code >= 400:
                print("✅ Invalid coordinates properly rejected")
            else:
                print(f"❌ Invalid coordinates should be rejected, got {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing invalid coordinates: {e}")

async def main():
    """Main test function"""
    print("NASA Weather Risk Detection API - Test Suite")
    print("=" * 50)
    
    async with APITester() as tester:
        # Run tests
        health_ok = await tester.test_health_check()
        
        if not health_ok:
            print("\n❌ Server health check failed. Is the server running?")
            print("Start the server with: python start_server.py")
            return
        
        locations = await tester.test_geocoding()
        
        if locations:
            await tester.test_weather_risk_analysis(locations)
        
        await tester.test_invalid_requests()
        
        print("\n" + "=" * 50)
        print("✅ Test suite completed!")
        print("🌐 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())