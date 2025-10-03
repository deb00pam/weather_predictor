import httpx
import asyncio
from typing import List, Dict, Optional
from urllib.parse import quote

class LocationService:
    """
    Location geocoding service using OpenStreetMap Nominatim API
    Converts place names to coordinates for NASA POWER API
    """
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.timeout = 10.0
        self.user_agent = "NASA-Weather-Risk-App/1.0"
    
    async def geocode(self, location_name: str, limit: int = 5) -> List[Dict]:
        """
        Convert location name to coordinates using OpenStreetMap Nominatim
        
        Args:
            location_name: Name of location to geocode
            limit: Maximum number of results to return
            
        Returns:
            List of location dictionaries with coordinates
        """
        # Validate input
        if not location_name or not location_name.strip():
            raise ValueError("Location name cannot be empty")
        
        try:
            # Validate input
            if not location_name or not location_name.strip():
                return []
            
            # Encode location name for URL
            encoded_location = quote(location_name.strip())
            
            # Build Nominatim API URL
            url = (
                f"{self.base_url}?"
                f"q={encoded_location}&"
                f"format=json&"
                f"addressdetails=1&"
                f"limit={limit}&"
                f"extratags=1"
            )
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                results = response.json()
                
                # Process and format results
                locations = self._process_nominatim_results(results)
                
                return locations
                
        except httpx.HTTPError as e:
            raise Exception(f"Nominatim geocoding request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error geocoding location: {str(e)}")
    
    def _process_nominatim_results(self, results: List[Dict]) -> List[Dict]:
        """
        Process Nominatim API results into standardized format
        """
        locations = []
        
        for result in results:
            try:
                # Extract address components
                address = result.get("address", {})
                
                # Build location name from address components
                name_parts = []
                
                # Add primary location identifiers
                for field in ["city", "town", "village", "hamlet", "municipality"]:
                    if field in address and address[field]:
                        name_parts.append(address[field])
                        break
                
                # Add state/region
                for field in ["state", "province", "region"]:
                    if field in address and address[field]:
                        name_parts.append(address[field])
                        break
                
                # Add country
                if "country" in address:
                    name_parts.append(address["country"])
                
                location_name = ", ".join(name_parts) if name_parts else result.get("display_name", "Unknown")
                
                location = {
                    "name": location_name,
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lon"]),
                    "country": address.get("country", "Unknown"),
                    "country_code": address.get("country_code", "").upper(),
                    "state": address.get("state", ""),
                    "city": self._get_city_name(address),
                    "display_name": result.get("display_name", ""),
                    "importance": float(result.get("importance", 0.0)),
                    "place_type": result.get("type", ""),
                    "osm_type": result.get("osm_type", ""),
                    "bounding_box": self._extract_bounding_box(result)
                }
                
                locations.append(location)
                
            except (ValueError, KeyError) as e:
                # Skip invalid results
                continue
        
        # Sort by importance (higher is better)
        locations.sort(key=lambda x: x["importance"], reverse=True)
        
        return locations
    
    def _get_city_name(self, address: Dict) -> str:
        """
        Extract the most appropriate city name from address components
        """
        city_fields = ["city", "town", "village", "hamlet", "municipality", "suburb"]
        
        for field in city_fields:
            if field in address and address[field]:
                return address[field]
        
        return ""
    
    def _extract_bounding_box(self, result: Dict) -> Optional[Dict]:
        """
        Extract bounding box coordinates if available
        """
        if "boundingbox" in result and len(result["boundingbox"]) == 4:
            try:
                bbox = result["boundingbox"]
                return {
                    "south": float(bbox[0]),
                    "north": float(bbox[1]), 
                    "west": float(bbox[2]),
                    "east": float(bbox[3])
                }
            except ValueError:
                return None
        
        return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Convert coordinates to location name (reverse geocoding)
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Location dictionary or None if not found
        """
        try:
            url = (
                f"https://nominatim.openstreetmap.org/reverse?"
                f"lat={latitude}&"
                f"lon={longitude}&"
                f"format=json&"
                f"addressdetails=1"
            )
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                
                if result:
                    locations = self._process_nominatim_results([result])
                    return locations[0] if locations else None
                
                return None
                
        except Exception as e:
            raise Exception(f"Error reverse geocoding coordinates: {str(e)}")
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate latitude and longitude coordinates
        
        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
            
        Returns:
            True if coordinates are valid
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)