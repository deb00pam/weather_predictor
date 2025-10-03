// API Client for NASA Weather Risk Detection
class WeatherRiskAPI {
  constructor() {
    this.baseURL = 'http://localhost:8000';
    this.timeout = 30000; // 30 seconds
  }

  // Check API health status
  async checkHealth() {
    try {
      const response = await axios.get(`${this.baseURL}/api/health`, {
        timeout: this.timeout
      });
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error('Unable to connect to weather risk API');
    }
  }

  // Geocode location name to coordinates
  async geocodeLocation(locationName) {
    try {
      const response = await axios.post(`${this.baseURL}/api/geocode`, {
        location_name: locationName
      }, {
        timeout: this.timeout
      });
      return response.data;
    } catch (error) {
      console.error('Geocoding failed:', error);
      if (error.response?.status === 404) {
        throw new Error('Location not found. Please try a different search term.');
      }
      throw new Error('Unable to search for location. Please check your connection.');
    }
  }

  // Analyze weather risk for location and dates
  async analyzeWeatherRisk(latitude, longitude, startDate, endDate, activityType = 'general') {
    try {
      const response = await axios.post(`${this.baseURL}/api/weather-risk`, {
        latitude: latitude,
        longitude: longitude,
        start_date: startDate,
        end_date: endDate,
        activity_type: activityType
      }, {
        timeout: this.timeout
      });
      return response.data;
    } catch (error) {
      console.error('Weather risk analysis failed:', error);
      if (error.response?.status === 500) {
        throw new Error('Weather analysis failed. The location may not have sufficient historical data.');
      }
      throw new Error('Unable to analyze weather risk. Please try again.');
    }
  }
}

// Create global API instance
window.weatherAPI = new WeatherRiskAPI();