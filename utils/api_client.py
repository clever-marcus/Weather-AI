import requests
import logging
from typing import Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """Client for interacting with the WeatherAI MCP API"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the API client
        
        Args:
            base_url: The base URL for the API
            api_key: Your WeatherAI API key
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Response as dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        # The MCP API uses a different URL structure
        # It's: https://api.weatherai.io/mcp?action=get_current_weather&location=London
        url = self.base_url
        
        # Always add apiKey to params
        if params is None:
            params = {}
        params['apiKey'] = self.api_key
        
        # Add the action to params
        params['action'] = endpoint
        
        logger.info(f"Making {method} request to {url} with params: {params}")
        
        try:
            response = self.session.request(method, url, params=params)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            # Try to parse JSON response
            try:
                return response.json()
            except ValueError:
                # If response is not JSON, return text
                return {"text": response.text, "status_code": response.status_code}
                
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (4xx, 5xx)
            logger.error(f"HTTP Error: {e}")
            error_data = {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
            try:
                error_data.update(response.json())
            except:
                pass
            return error_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            return {
                "error": True,
                "status_code": 500,
                "message": str(e)
            }
    
    def get_current_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather for a location
        
        Args:
            location: City name or coordinates
            units: "metric" or "imperial"
            
        Returns:
            Weather data as dictionary
        """
        params = {
            "location": location,
            "units": units
        }
        return self._make_request("GET", "get_current_weather", params)
    
    def get_weather_forecast(self, location: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name or coordinates
            days: Number of days to forecast (1-10)
            units: "metric" or "imperial"
            
        Returns:
            Forecast data as dictionary
        """
        params = {
            "location": location,
            "days": days,
            "units": units
        }
        return self._make_request("GET", "get_weather_forecast", params)
    
    def get_historical_weather(self, location: str, date: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get historical weather for a location on a specific date
        
        Args:
            location: City name or coordinates
            date: Date in YYYY-MM-DD format
            units: "metric" or "imperial"
            
        Returns:
            Historical weather data as dictionary
        """
        params = {
            "location": location,
            "date": date,
            "units": units
        }
        return self._make_request("GET", "get_historical_weather", params)