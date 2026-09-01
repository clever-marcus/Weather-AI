import pytest
import os
from dotenv import load_dotenv
from utils.api_client import WeatherAPIClient

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def api_client():
    """Provides a configured API client for all tests"""
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = os.getenv("BASE_URL", "https://api.weatherai.io/mcp")
    
    if not api_key:
        pytest.fail("WEATHER_API_KEY not found in environment variables. Please check your .env file.")
    
    return WeatherAPIClient(base_url, api_key)


@pytest.fixture
def test_cities():
    """Provides a list of test cities"""
    return ["London", "New York", "Tokyo", "Sydney"]


@pytest.fixture
def invalid_cities():
    """Provides invalid city names for edge cases"""
    return ["", "InvalidCity123", "CityWithVeryLongNameThatDoesntExist"]