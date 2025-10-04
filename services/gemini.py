import google.generativeai as genai
from typing import Dict, Optional, List
import json
from config import Config

class GeminiService:
    """Service to interact with Google Gemini AI for weather analysis"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key not found")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def analyze_weather_for_activities(self, location_info: Dict, weather_data: Dict, 
                                     weather_analysis: Dict, user_query: str) -> str:
        """
        Analyze weather data and provide activity recommendations
        
        Args:
            location_info: Location details from location service
            weather_data: Raw weather data from NASA POWER
            weather_analysis: Processed weather analysis
            user_query: Original user query
            
        Returns:
            AI-generated response with weather analysis and recommendations
        """
        try:
            # Check data quality first
            data_quality = weather_analysis.get('data_quality', 'unknown')
            valid_points = weather_analysis.get('valid_data_points', 0)
            total_points = weather_analysis.get('total_days', 0)
            
            if data_quality == 'poor' or valid_points < 3:
                return self._create_climate_based_response(location_info, user_query)
            
            prompt = self._create_weather_analysis_prompt(
                location_info, weather_data, weather_analysis, user_query
            )
            
            print(f"🤖 Sending request to Gemini for location: {location_info.get('name', 'Unknown')}")
            print(f"📊 Data quality: {data_quality} ({valid_points}/{total_points} valid points)")
            response = self.model.generate_content(prompt)
            print("✅ Gemini response received successfully")
            return response.text
            
        except Exception as e:
            print(f"❌ Error generating Gemini response: {e}")
            print(f"📍 Location: {location_info.get('name', 'Unknown')}")
            print(f"📊 Weather analysis keys: {list(weather_analysis.keys())}")
            return self._create_climate_based_response(location_info, user_query)
    
    def _create_weather_analysis_prompt(self, location_info: Dict, weather_data: Dict, 
                                      weather_analysis: Dict, user_query: str) -> str:
        """Create a comprehensive prompt for Gemini analysis"""
        
        location_name = location_info.get('name', 'the specified location')
        full_address = location_info.get('full_address', 'Unknown location')
        
        # Format weather statistics
        stats = f"""
Recent Weather Data for {location_name}:
- Location: {full_address}
- Days analyzed: {weather_analysis.get('total_days', 0)}
- Average temperature: {weather_analysis.get('avg_temperature', 0):.1f}°C
- Average precipitation: {weather_analysis.get('avg_precipitation', 0):.1f}mm/day
- Average wind speed: {weather_analysis.get('avg_wind_speed', 0):.1f}m/s
- Average humidity: {weather_analysis.get('avg_humidity', 0):.1f}%

Extreme Weather Days:
- Very hot days (>35°C): {weather_analysis.get('very_hot_days', 0)}
- Very cold days (<0°C): {weather_analysis.get('very_cold_days', 0)}
- Very windy days (>15m/s): {weather_analysis.get('very_windy_days', 0)}
- Very wet days (>10mm): {weather_analysis.get('very_wet_days', 0)}
- Very uncomfortable days: {weather_analysis.get('very_uncomfortable_days', 0)}
"""
        
        prompt = f"""
You are a friendly, helpful weather buddy who loves talking about outdoor activities! A friend just asked you: "{user_query}"

Here's what the recent weather has been like:
{stats}

Respond like you're chatting with a friend who's planning their day out. Be conversational, enthusiastic, and helpful! 

Make sure to:
🗣️ **Be Conversational**: Talk like you're texting a friend, not writing a weather report
😊 **Be Enthusiastic**: Show excitement about their plans and the weather
🎯 **Be Specific**: Give practical, actionable advice for their exact activity
🌍 **Be Local**: Mention things specific to {location_name} if you know them
💬 **Be Casual**: Use friendly language, contractions, and a warm tone

Structure your response like:
1. **Friendly greeting** - acknowledge what they want to do
2. **Weather chat** - talk about the current conditions in a conversational way
3. **Activity advice** - specific tips for their planned activity
4. **Local tips** - any location-specific advice
5. **Encouragement** - end on a positive, motivating note

Remember: You're their weather-savvy friend, not a meteorologist! Keep it fun and helpful.
"""
        
        return prompt
        
        return prompt
    
    def _create_climate_based_response(self, location_info: Dict, user_query: str) -> str:
        """Create a response based on general climate knowledge when data is poor"""
        location_name = location_info.get('name', '').lower()
        country = location_info.get('country', '').lower()
        
        try:
            prompt = f"""
Hey! Your friend just asked: "{user_query}"

They want to know about {location_info.get('name', 'Unknown location')} ({location_info.get('full_address', '')})

The weather data is acting up right now (showing some weird numbers), but I still want to help them plan their activity! 

As their weather-savvy friend, give them advice based on what you know about this location's typical climate. 

Be super conversational and friendly - like you're texting them back! Include:

🌤️ **Climate Chat**: "So here's the thing about {location_info.get('name', 'that place')}..." - what's the weather usually like there?

🎯 **Activity Advice**: Based on what they want to do, give them practical tips

📅 **Timing Tips**: When's the best time for their activity?

🎒 **What to Pack**: Practical packing advice

💬 **Data Note**: Casually mention the data is being wonky, but you've got their back with local climate knowledge

Keep it fun, helpful, and conversational - like you're their local friend who knows the area!
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Error with climate-based response: {e}")
            return self._create_basic_climate_fallback(location_info, user_query)
    
    def _create_basic_climate_fallback(self, location_info: Dict, user_query: str) -> str:
        """Basic fallback when even Gemini fails"""
        location_name = location_info.get('name', 'that spot')
        
        return f"""Hey there! 😊 I'd totally love to help you plan your adventure in {location_name}! 

**Quick heads up**: The weather data is being a bit wonky right now (showing some crazy impossible numbers), so I can't give you the usual detailed analysis.

**But here's what I'd suggest**:
🌤️ Definitely check your local weather app before heading out - they'll have the most up-to-date info for {location_name}
📅 Think about what time of year it typically is there - you probably know the usual patterns better than anyone!
🎒 Pack smart - bring layers, water, and maybe rain gear just in case
☀️ Always good to have sun protection too

**I'm bummed** the weather data isn't cooperating right now, but don't let that stop your plans! Local weather services will have your back with the real-time conditions.

Hope you have an awesome time out there! 🌟"""
    
    def get_location_specific_activities(self, location_info: Dict) -> List[str]:
        """Get location-specific activity suggestions from Gemini"""
        try:
            location_name = location_info.get('name', 'the location')
            full_address = location_info.get('full_address', '')
            
            prompt = f"""
What are the most popular and suitable outdoor activities for {location_name} ({full_address})?
Consider the geographic features, local attractions, and typical activities people do there.
Provide a list of 5-10 specific activities, focusing on outdoor and weather-dependent activities.
Format as a simple comma-separated list.
"""
            
            response = self.model.generate_content(prompt)
            activities_text = response.text.strip()
            
            # Parse the response into a list
            activities = [activity.strip() for activity in activities_text.split(',')]
            return activities[:10]  # Limit to 10 activities
            
        except Exception as e:
            print(f"Error getting location activities: {e}")
            return self._get_default_activities()
    
    def _get_default_activities(self) -> List[str]:
        """Default activities if Gemini fails"""
        return [
            "hiking", "camping", "picnicking", "photography", "sightseeing",
            "outdoor sports", "cycling", "walking", "fishing", "bird watching"
        ]
    
    def _create_fallback_response(self, weather_analysis: Dict, location_info: Dict) -> str:
        """Create a fallback response if Gemini fails"""
        location_name = location_info.get('name', 'the location')
        
        response = f"Weather Analysis for {location_name}:\n\n"
        
        # Temperature analysis
        avg_temp = weather_analysis.get('avg_temperature', 0)
        if avg_temp > 30:
            response += "🌡️ **Temperature**: Quite warm with average temperatures above 30°C. Consider early morning or evening activities.\n\n"
        elif avg_temp < 10:
            response += "🌡️ **Temperature**: Cool conditions with average temperatures below 10°C. Dress warmly for outdoor activities.\n\n"
        else:
            response += f"🌡️ **Temperature**: Pleasant conditions with average temperature around {avg_temp:.1f}°C.\n\n"
        
        # Precipitation analysis
        avg_precip = weather_analysis.get('avg_precipitation', 0)
        wet_days = weather_analysis.get('very_wet_days', 0)
        if wet_days > weather_analysis.get('total_days', 1) * 0.3:
            response += "🌧️ **Precipitation**: Frequent rain expected. Pack waterproof gear and have indoor backup plans.\n\n"
        elif avg_precip > 5:
            response += "🌧️ **Precipitation**: Moderate rainfall. Light rain gear recommended.\n\n"
        else:
            response += "☀️ **Precipitation**: Generally dry conditions. Good for most outdoor activities.\n\n"
        
        # Wind analysis
        windy_days = weather_analysis.get('very_windy_days', 0)
        if windy_days > 0:
            response += f"💨 **Wind**: Expect {windy_days} very windy days. Be cautious with activities like camping or cycling.\n\n"
        
        response += "**Recommendations**: Check current forecasts before your trip and pack appropriately for the conditions!"
        
        return response