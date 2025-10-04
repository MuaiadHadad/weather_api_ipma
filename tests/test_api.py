import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.models import DailyForecast, HourlyForecast, WeatherCondition, Location

client = TestClient(app)


class TestForecastAPI:

    @pytest.fixture
    def mock_forecast(self):
        return DailyForecast(
            date="2025-10-04",
            location="Lisboa",
            district="Lisboa",
            hourly_forecasts=[
                HourlyForecast(
                    hour="12:00",
                    temperature=22.5,
                    weather_condition=WeatherCondition(id=1, description="Céu limpo"),
                    precipitation_probability=10,
                    wind_speed=15.2,
                    wind_direction="NW"
                )
            ],
            min_temperature=18.0,
            max_temperature=25.0
        )

    @pytest.fixture
    def mock_locations(self):
        return [
            Location(id=1110600, name="Lisboa", district="Lisboa"),
            Location(id=1110601, name="Cascais", district="Lisboa")
        ]

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Weather API IPMA"
        assert "endpoints" in data
        assert "examples" in data

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch('app.routers.forecast.ipma_service.get_forecast_for_location')
    def test_get_forecast_current_success(self, mock_get_forecast, mock_forecast):
        mock_get_forecast.return_value = mock_forecast

        response = client.get("/forecast/lisboa/lisboa")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["location"] == "Lisboa"
        assert data["data"]["district"] == "Lisboa"
        assert len(data["data"]["hourly_forecasts"]) == 1

    @patch('app.routers.forecast.ipma_service.get_forecast_for_location')
    @patch('app.routers.forecast.ipma_service.get_locations_by_district')
    def test_get_forecast_current_district_not_found(self, mock_get_locations, mock_get_forecast):
        mock_get_forecast.return_value = None
        mock_get_locations.return_value = []

        response = client.get("/forecast/inexistente/lisboa")
        assert response.status_code == 404

        data = response.json()
        assert "Distrito 'inexistente' não encontrado" in data["detail"]

    @patch('app.routers.forecast.ipma_service.get_forecast_for_location')
    @patch('app.routers.forecast.ipma_service.get_locations_by_district')
    def test_get_forecast_current_location_not_found(self, mock_get_locations, mock_get_forecast, mock_locations):
        mock_get_forecast.return_value = None
        mock_get_locations.return_value = mock_locations

        response = client.get("/forecast/lisboa/inexistente")
        assert response.status_code == 404

        data = response.json()
        assert "Localidade 'inexistente' não encontrada" in data["detail"]

    @patch('app.routers.forecast.ipma_service.get_forecast_for_location')
    def test_get_forecast_by_date_success(self, mock_get_forecast, mock_forecast):
        mock_get_forecast.return_value = mock_forecast

        response = client.get("/forecast/lisboa/lisboa/?day=2025-10-04")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["date"] == "2025-10-04"

    def test_get_forecast_by_date_invalid_format(self):
        response = client.get("/forecast/lisboa/lisboa/?day=invalid-date")
        assert response.status_code == 422

    @patch('app.routers.forecast.ipma_service.get_locations_by_district')
    def test_get_locations_by_district_success(self, mock_get_locations, mock_locations):
        mock_get_locations.return_value = mock_locations

        response = client.get("/forecast/lisboa")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Lisboa"
        assert data["data"][1]["name"] == "Cascais"

    @patch('app.routers.forecast.ipma_service.get_locations_by_district')
    def test_get_locations_by_district_not_found(self, mock_get_locations):
        mock_get_locations.return_value = []

        response = client.get("/forecast/inexistente")
        assert response.status_code == 404

        data = response.json()
        assert "Distrito 'inexistente' não encontrado" in data["detail"]

    @patch('app.routers.forecast.ipma_service.get_districts_and_locations')
    def test_get_available_districts(self, mock_get_districts):
        mock_get_districts.return_value = {
            "lisboa": [],
            "porto": [],
            "faro": []
        }

        response = client.get("/forecast/")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["districts"]) == 3
        assert "lisboa" in data["data"]["districts"]
        assert "porto" in data["data"]["districts"]
        assert "faro" in data["data"]["districts"]
