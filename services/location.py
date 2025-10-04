from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Optional, Tuple, Dict
import time

class LocationService:
    """Service to handle location queries using OpenStreetMap/Nominatim"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="weather_predictor_chatbot")
    
    def get_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Convert location name to coordinates
        
        Args:
            location_name: Name of the location (e.g., "New York", "Paris, France")
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Add a small delay to respect rate limits
            time.sleep(1)
            
            location = self.geolocator.geocode(location_name, timeout=10)
            
            if location:
                return (location.latitude, location.longitude)
            else:
                print(f"Location '{location_name}' not found")
                return None
                
        except GeocoderTimedOut:
            print(f"Geocoding timeout for '{location_name}'")
            return None
        except GeocoderServiceError as e:
            print(f"Geocoding service error: {e}")
            return None
        except Exception as e:
            print(f"Error geocoding '{location_name}': {e}")
            return None
    
    def get_location_info(self, location_name: str) -> Optional[Dict]:
        """
        Get detailed location information
        
        Args:
            location_name: Name of the location
            
        Returns:
            Dictionary with location details or None if not found
        """
        try:
            time.sleep(1)
            
            location = self.geolocator.geocode(location_name, timeout=10)
            
            if location:
                # Parse the address components
                address_parts = location.address.split(', ')
                
                return {
                    'name': location_name,
                    'full_address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'country': address_parts[-1] if len(address_parts) > 0 else None,
                    'state_province': address_parts[-2] if len(address_parts) > 1 else None,
                    'city': address_parts[0] if len(address_parts) > 0 else None
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error getting location info for '{location_name}': {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates back to location name
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Location name or None if not found
        """
        try:
            time.sleep(1)
            
            location = self.geolocator.reverse((latitude, longitude), timeout=10)
            
            if location:
                return location.address
            else:
                return None
                
        except Exception as e:
            print(f"Error reverse geocoding ({latitude}, {longitude}): {e}")
            return None
    
    def extract_location_from_text(self, text: str) -> Optional[str]:
        """
        Simple extraction of location from user text
        This is a basic implementation - could be enhanced with NLP
        
        Args:
            text: User input text
            
        Returns:
            Extracted location string or None
        """
        # Common location indicators
        location_keywords = [
            'in ', 'at ', 'near ', 'around ', 'for ', 'to ',
            'visit ', 'go to ', 'travel to ', 'vacation in '
        ]
        
        text_lower = text.lower()
        
        # Look for patterns like "hiking in Colorado" or "camping near Yellowstone"
        for keyword in location_keywords:
            if keyword in text_lower:
                # Find the position of the keyword
                start_idx = text_lower.find(keyword) + len(keyword)
                
                # Extract text after the keyword until punctuation or end
                remaining_text = text[start_idx:].strip()
                
                # Take words until we hit common stop words or punctuation
                stop_words = ['this', 'next', 'week', 'weekend', 'month', 'year', 
                             'tomorrow', 'today', 'on', 'during', 'for', 'and', 'or']
                
                location_words = []
                for word in remaining_text.split():
                    # Remove punctuation and check if it's a stop word
                    clean_word = word.strip('.,!?;:')
                    if clean_word.lower() in stop_words:
                        break
                    location_words.append(word)
                    
                    # Limit to reasonable location length (3 words max)
                    if len(location_words) >= 3:
                        break
                
                if location_words:
                    location = ' '.join(location_words)
                    # Clean up any remaining punctuation
                    location = location.strip('.,!?;:')
                    return location
        
        # If no pattern found, look for common location patterns
        # This is a simplified approach - a full NLP solution would be better
        words = text.split()
        for i, word in enumerate(words):
            # Look for capitalized words that might be places
            if word[0].isupper() and i < len(words) - 1:
                # Check if next word is also capitalized (like "New York")
                next_words = []
                for j in range(i, min(i + 3, len(words))):
                    if words[j][0].isupper():
                        next_words.append(words[j])
                    else:
                        break
                
                if len(next_words) > 0:
                    potential_location = ' '.join(next_words)
                    # Remove punctuation
                    potential_location = potential_location.strip('.,!?;:')
                    if len(potential_location) > 2:  # Must be reasonable length
                        return potential_location
        
        return None