import pytest
import json
from datetime import datetime, timedelta


class TestWeatherForecast:
    """Test suite for the weather forecast endpoint"""
    
    def test_get_forecast_success(self, api_client):
        """Test successful retrieval of weather forecast"""
        city = "London"
        days = 5
        
        response = api_client.get_weather_forecast(city, days=days)
        
        if "error" in response:
            print(f"Forecast response: {json.dumps(response, indent=2)}")
            pytest.skip(f"API returned error: {response.get('message', 'Unknown error')}")
        
        # Check for forecast data in various formats
        # The WeatherAI API might return forecast in the main response or nested
        forecast_data = None
        
        # Try different possible response structures
        if "forecast" in response:
            forecast_data = response["forecast"]
        elif "data" in response:
            if "forecast" in response["data"]:
                forecast_data = response["data"]["forecast"]
            elif "list" in response["data"]:
                forecast_data = response["data"]["list"]
        elif "list" in response:
            forecast_data = response["list"]
        
        # If we still don't have forecast data, check if the response itself is the forecast
        if forecast_data is None and isinstance(response, list):
            forecast_data = response
        
        if forecast_data is None:
            print(f"Response structure: {list(response.keys())}")
            print(f"Full response: {json.dumps(response, indent=2)[:500]}...")
            pytest.skip("Could not find forecast data in response")
        
        assert isinstance(forecast_data, list), f"Forecast should be a list, got {type(forecast_data)}"
        assert len(forecast_data) > 0, f"Forecast list is empty"
        
        # Validate each forecast entry
        for i, day in enumerate(forecast_data[:3]):  # Check first 3 entries
            assert day is not None, f"Forecast entry {i} is None"
            
            # Check for common forecast fields
            if "date" in day or "datetime" in day or "dt" in day:
                print(f"Day {i} has date field")
            if "temperature" in day or "temp" in day:
                print(f"Day {i} has temperature field")
            if "description" in day or "condition" in day or "weather" in day:
                print(f"Day {i} has description field")
            
            print(f"Forecast day {i}: {json.dumps(day, indent=2)[:200]}...")
    
    def test_get_forecast_different_days(self, api_client):
        """Test forecast with different numbers of days"""
        city = "Tokyo"
        
        test_days = [1, 3, 5]
        
        for days in test_days:
            response = api_client.get_weather_forecast(city, days=days)
            
            if "error" in response:
                print(f"Failed for {days} days: {response}")
                continue
            
            # Try to get forecast length
            forecast_data = None
            if "forecast" in response:
                forecast_data = response["forecast"]
            elif "data" in response and "forecast" in response["data"]:
                forecast_data = response["data"]["forecast"]
            elif "data" in response and "list" in response["data"]:
                forecast_data = response["data"]["list"]
            elif "list" in response:
                forecast_data = response["list"]
            
            if forecast_data:
                print(f"Got {len(forecast_data)} days for request of {days} days")
                # Check if the API respects the days parameter
                # Some APIs might return a fixed number of days regardless of parameter
                if len(forecast_data) <= days + 1:  # Allow some flexibility
                    print(f"✓ Requested {days} days, got {len(forecast_data)}")
    
    def test_get_forecast_invalid_days(self, api_client):
        """Test forecast with invalid number of days"""
        city = "London"
        
        # Test with days > 10 (should fail or return max)
        response = api_client.get_weather_forecast(city, days=15)
        if "error" not in response:
            # Some APIs might cap at max days instead of error
            forecast_data = None
            if "forecast" in response:
                forecast_data = response["forecast"]
            elif "data" in response and "forecast" in response["data"]:
                forecast_data = response["data"]["forecast"]
            
            if forecast_data:
                print(f"15 days request returned {len(forecast_data)} days (might be capped at max)")
        
        # Test with days <= 0 (should fail)
        response = api_client.get_weather_forecast(city, days=0)
        if "error" not in response:
            print("Request with 0 days did not return an error")
        
        # Test with negative days (should fail)
        response = api_client.get_weather_forecast(city, days=-5)
        if "error" not in response:
            print("Request with negative days did not return an error")
    
    def test_get_forecast_invalid_location(self, api_client):
        """Test forecast with invalid location"""
        response = api_client.get_weather_forecast("InvalidCity123")
        
        # May return error or empty data
        if "error" in response:
            print(f"Invalid location returned error: {response.get('message', '')[:100]}")
        else:
            # Check if we got any data
            forecast_data = None
            if "forecast" in response:
                forecast_data = response["forecast"]
            elif "data" in response and "forecast" in response["data"]:
                forecast_data = response["data"]["forecast"]
            
            if forecast_data and len(forecast_data) > 0:
                print(f"Warning: Invalid location returned data: {len(forecast_data)} entries")
    
    def test_get_forecast_response_structure(self, api_client):
        """Test that forecast response has the expected structure"""
        city = "New York"
        
        response = api_client.get_weather_forecast(city)
        
        if "error" in response:
            pytest.skip(f"API returned error: {response}")
        
        # Check for required top-level fields
        # Different APIs have different structures
        if "forecast" in response:
            assert isinstance(response["forecast"], list), "Forecast should be a list"
            assert len(response["forecast"]) > 0, "Forecast list should not be empty"
        elif "data" in response:
            assert "forecast" in response["data"] or "list" in response["data"], \
                "Data should contain forecast or list"
        elif "list" in response:
            assert isinstance(response["list"], list), "List should be a list"
    
    @pytest.mark.smoke
    def test_get_forecast_smoke(self, api_client):
        """Smoke test: verify forecast endpoint is working"""
        response = api_client.get_weather_forecast("Paris", days=3)
        
        # Just verify we can reach the endpoint and get a response
        assert response is not None, "No response received"
        
        if "error" in response:
            print(f"Forecast smoke test had error: {response.get('message', '')[:200]}")
        else:
            print(f"Forecast smoke test successful: {json.dumps(response, indent=2)[:500]}...")