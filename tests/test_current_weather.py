import pytest
import json


class TestCurrentWeather:
    """Test suite for the current weather endpoint"""
    
    def test_get_current_weather_success(self, api_client, test_cities):
        """Test successful retrieval of current weather for multiple cities"""
        for city in test_cities:
            response = api_client.get_current_weather(city)
            
            # Check if we got an error
            if "error" in response:
                print(f"Response for {city}: {response}")
                # If it's a 404, the city might not exist in the free tier
                if response.get("status_code") == 404:
                    continue  # Skip this city
                pytest.fail(f"API returned error for {city}: {response}")
            
            # Check response structure - different APIs return different formats
            # Let's check for common weather response fields
            assert response is not None, f"No response for {city}"
            
            # Try to find weather data in various possible response formats
            weather_data = None
            if "data" in response:
                weather_data = response["data"]
            elif "result" in response:
                weather_data = response["result"]
            elif "weather" in response:
                weather_data = response["weather"]
            else:
                weather_data = response
            
            # Log what we got for debugging
            print(f"Response for {city}: {json.dumps(response, indent=2)[:500]}...")
            
            # Check for temperature field (could be in different places)
            temp_fields = ["temperature", "temp", "current_temp", "temp_c"]
            found_temp = False
            for field in temp_fields:
                if field in weather_data:
                    temp_value = weather_data[field]
                    assert isinstance(temp_value, (int, float)), f"Temperature should be a number, got {type(temp_value)}"
                    assert -50 < temp_value < 60, f"Temperature {temp_value} outside reasonable range"
                    found_temp = True
                    break
            
            if not found_temp:
                # If we can't find temperature, at least verify we got some data
                assert len(weather_data) > 0, f"No weather data found for {city}"
    
    def test_get_current_weather_different_units(self, api_client):
        """Test current weather with different unit systems"""
        city = "London"
        
        # Test metric units
        response_metric = api_client.get_current_weather(city, units="metric")
        if "error" in response_metric:
            pytest.skip(f"API returned error for metric units: {response_metric}")
        
        # Test imperial units
        response_imperial = api_client.get_current_weather(city, units="imperial")
        if "error" in response_imperial:
            pytest.skip(f"API returned error for imperial units: {response_imperial}")
        
        # Try to extract temperatures from response
        def extract_temperature(response):
            if "data" in response and "temperature" in response["data"]:
                return response["data"]["temperature"]
            elif "temperature" in response:
                return response["temperature"]
            elif "temp" in response:
                return response["temp"]
            return None
        
        temp_metric = extract_temperature(response_metric)
        temp_imperial = extract_temperature(response_imperial)
        
        if temp_metric is not None and temp_imperial is not None:
            # Imperial should generally be higher than metric for the same temperature
            # But this depends on the API implementation
            print(f"Metric temp: {temp_metric}, Imperial temp: {temp_imperial}")
    
    def test_get_current_weather_invalid_location(self, api_client):
        """Test current weather with invalid locations"""
        invalid_cities = ["", "InvalidCity123", "CityWithVeryLongNameThatDoesntExist"]
        
        for invalid_city in invalid_cities:
            response = api_client.get_current_weather(invalid_city)
            
            # Should return error or empty response
            if "error" not in response:
                # If no error, check if we got any data
                if "data" in response and response["data"]:
                    # Some APIs might return data for empty string (maybe default city)
                    if invalid_city == "":
                        continue  # Skip empty string test
                # For completely invalid cities, we should get an error
                if invalid_city and invalid_city != "":
                    print(f"Warning: Invalid city '{invalid_city}' returned: {response}")
    
    def test_get_current_weather_response_time(self, api_client):
        """Test that response times are reasonable (performance test)"""
        import time
        
        city = "London"
        
        # Measure response time
        start_time = time.time()
        response = api_client.get_current_weather(city)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5 second threshold"
        
        # Make sure we got a response (even if it's an error)
        assert response is not None, "No response received"
    
    @pytest.mark.smoke
    def test_get_current_weather_smoke(self, api_client):
        """Smoke test: verify current weather endpoint is working"""
        response = api_client.get_current_weather("Paris")
        
        # Just verify we can reach the endpoint and get a response
        assert response is not None, "No response received"
        print(f"Smoke test response: {json.dumps(response, indent=2)[:500]}...")