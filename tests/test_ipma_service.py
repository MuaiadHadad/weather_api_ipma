import pytest
from unittest.mock import Mock, patch
from app.services.ipma_service import IPMAService
from app.models import Location, DailyForecast


class TestIPMAService:

    @pytest.fixture
    def ipma_service(self):
        return IPMAService()

    @pytest.fixture
    def mock_districts_response(self):
        return {
            "data": [
                {
                    "idAreaAviso": 1,
                    "description": "Lisboa"
                },
                {
                    "idAreaAviso": 2,
                    "description": "Porto"
                }
            ]
        }

    @pytest.fixture
    def mock_locations_response(self):
        return {
            "data": [
                {
                    "globalIdLocal": 1110600,
                    "local": "Lisboa",
                    "district": "Lisboa"
                },
                {
                    "globalIdLocal": 1110601,
                    "local": "Cascais",
                    "district": "Lisboa"
                }
            ]
        }

    @pytest.fixture
    def mock_forecast_response(self):
        return {
            "data": [
                {
                    "forecastDate": "2025-10-04T12:00:00",
                    "tMed": 22.5,
                    "idWeatherType": 1,
                    "probabilityOfPrecipitation": 10,
                    "ffVento": 15.2,
                    "ddVento": "NW"
                }
            ]
        }

    @pytest.fixture
    def mock_weather_conditions(self):
        return {
            "data": [
                {
                    "idWeatherType": 1,
                    "descIdWeatherTypePT": "Céu limpo"
                }
            ]
        }

    @patch('app.services.ipma_service.requests.Session.get')
    def test_get_districts_and_locations(self, mock_get, ipma_service, mock_districts_response, mock_locations_response):
        # Mock das respostas da API
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: mock_districts_response),
            Mock(status_code=200, json=lambda: mock_locations_response),
            Mock(status_code=200, json=lambda: mock_locations_response)
        ]

        # Limpar cache
        ipma_service.get_districts_and_locations.cache_clear()

        result = ipma_service.get_districts_and_locations()

        assert "lisboa" in result
        assert len(result["lisboa"]) == 2
        assert result["lisboa"][0].name == "Lisboa"
        assert result["lisboa"][1].name == "Cascais"

    @patch('app.services.ipma_service.requests.Session.get')
    def test_get_weather_conditions(self, mock_get, ipma_service, mock_weather_conditions):
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_weather_conditions)

        # Limpar cache
        ipma_service.get_weather_conditions.cache_clear()

        result = ipma_service.get_weather_conditions()

        assert 1 in result
        assert result[1] == "Céu limpo"

    def test_find_location_id(self, ipma_service):
        # Mock do método get_districts_and_locations
        mock_locations = {
            "lisboa": [
                Location(id=1110600, name="Lisboa", district="Lisboa"),
                Location(id=1110601, name="Cascais", district="Lisboa")
            ]
        }

        with patch.object(ipma_service, 'get_districts_and_locations', return_value=mock_locations):
            location_id = ipma_service.find_location_id("lisboa", "cascais")
            assert location_id == 1110601

            # Teste para localidade inexistente
            location_id = ipma_service.find_location_id("lisboa", "inexistente")
            assert location_id is None

            # Teste para distrito inexistente
            location_id = ipma_service.find_location_id("inexistente", "cascais")
            assert location_id is None

    @patch('app.services.ipma_service.requests.Session.get')
    def test_get_forecast(self, mock_get, ipma_service, mock_forecast_response):
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_forecast_response)

        # Limpar cache
        ipma_service.get_forecast.cache_clear()

        result = ipma_service.get_forecast(1110600)

        assert result is not None
        assert "data" in result
        assert len(result["data"]) == 1

    def test_parse_forecast_data(self, ipma_service, mock_forecast_response):
        # Mock do método get_weather_conditions
        mock_conditions = {1: "Céu limpo"}

        with patch.object(ipma_service, 'get_weather_conditions', return_value=mock_conditions):
            result = ipma_service.parse_forecast_data(
                mock_forecast_response, "Lisboa", "Lisboa", "2025-10-04"
            )

            assert result is not None
            assert isinstance(result, DailyForecast)
            assert result.location == "Lisboa"
            assert result.district == "Lisboa"
            assert result.date == "2025-10-04"
            assert len(result.hourly_forecasts) == 1
            assert result.hourly_forecasts[0].temperature == 22.5
            assert result.hourly_forecasts[0].weather_condition.description == "Céu limpo"

    def test_get_locations_by_district(self, ipma_service):
        # Mock do método get_districts_and_locations
        mock_locations = {
            "lisboa": [
                Location(id=1110600, name="Lisboa", district="Lisboa"),
                Location(id=1110601, name="Cascais", district="Lisboa")
            ]
        }

        with patch.object(ipma_service, 'get_districts_and_locations', return_value=mock_locations):
            locations = ipma_service.get_locations_by_district("lisboa")
            assert len(locations) == 2
            assert locations[0].name == "Lisboa"
            assert locations[1].name == "Cascais"

            # Teste para distrito inexistente
            locations = ipma_service.get_locations_by_district("inexistente")
            assert len(locations) == 0
