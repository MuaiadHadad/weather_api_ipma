import requests
import json
import csv
from typing import List, Optional, Dict, Any
from functools import lru_cache
from datetime import datetime, timedelta
from app.models import (
    DailyForecast, HourlyForecast, WeatherCondition, Location,
    WeatherWarning, SeismicData, SeaState, FireRisk, UVIndex,
    WeatherStation, StationObservation, AgriculturalData, WaterQuality
)
import logging

logger = logging.getLogger(__name__)


class IPMAService:
    """Serviço completo para interação com TODOS os recursos da API do IPMA"""

    BASE_URL = "https://api.ipma.pt/open-data"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'weather_api_ipma/2.0'
        })

    # ==================== MÉTODOS ORIGINAIS ====================

    @lru_cache(maxsize=128, typed=True)
    def get_districts_and_locations(self) -> Dict[str, List[Location]]:
        """Obtém lista de distritos e localidades com cache"""
        try:
            response = self.session.get(f"{self.BASE_URL}/distrits-islands.json")
            response.raise_for_status()

            data = response.json()
            districts_locations = {}

            for location_data in data.get('data', []):
                district_name = self._get_district_name(location_data.get('idDistrito', 0))
                if not district_name:
                    continue

                location = Location(
                    id=location_data.get('globalIdLocal'),
                    name=location_data.get('local', '').strip(),
                    district=district_name
                )

                district_key = district_name.lower()
                if district_key not in districts_locations:
                    districts_locations[district_key] = []

                districts_locations[district_key].append(location)

            return districts_locations

        except Exception as e:
            logger.error(f"Erro ao obter distritos e localidades: {e}")
            return {}

    def _get_district_name(self, district_id: int) -> str:
        """Mapeia ID do distrito para nome"""
        district_map = {
            1: "Aveiro", 2: "Beja", 3: "Braga", 4: "Bragança", 5: "Castelo Branco",
            6: "Coimbra", 7: "Évora", 8: "Faro", 9: "Guarda", 10: "Leiria",
            11: "Lisboa", 12: "Portalegre", 13: "Porto", 14: "Santarém", 15: "Setúbal",
            16: "Viana do Castelo", 17: "Vila Real", 18: "Viseu",
            31: "Ilha da Madeira", 32: "Ilha de Porto Santo",
            41: "Ilha de Santa Maria", 42: "Ilha de São Miguel", 43: "Ilha Terceira",
            44: "Ilha da Graciosa", 45: "Ilha de São Jorge", 46: "Ilha do Pico",
            47: "Ilha do Faial", 48: "Ilha das Flores", 49: "Ilha do Corvo"
        }
        return district_map.get(district_id, "")

    @lru_cache(maxsize=256, typed=True)
    def get_weather_conditions(self) -> Dict[int, str]:
        """Obtém dicionário de condições meteorológicas com cache"""
        try:
            response = self.session.get(f"{self.BASE_URL}/weather-type-classe.json")
            response.raise_for_status()

            data = response.json()
            conditions = {}

            for condition in data.get('data', []):
                conditions[condition.get('idWeatherType')] = condition.get('descIdWeatherTypePT', 'Desconhecido')

            return conditions

        except Exception as e:
            logger.error(f"Erro ao obter condições meteorológicas: {e}")
            return {}

    # ==================== NOVOS RECURSOS EXPANDIDOS ====================

    @lru_cache(maxsize=64, typed=True)
    def get_weather_warnings(self, days: int = 3) -> List[WeatherWarning]:
        """Obtém avisos meteorológicos até 3 dias"""
        try:
            response = self.session.get(f"{self.BASE_URL}/warnings/warnings_www.json")
            response.raise_for_status()

            data = response.json()
            warnings = []

            for warning_data in data.get('data', []):
                warning = WeatherWarning(
                    id=str(warning_data.get('idAreaAviso', '')),
                    area=warning_data.get('area', ''),
                    warning_type=warning_data.get('awarenessTypeName', ''),
                    level=self._get_warning_level(warning_data.get('awarenessLevelID', 0)),
                    start_time=warning_data.get('startTime', ''),
                    end_time=warning_data.get('endTime', ''),
                    description=warning_data.get('text', ''),
                    phenomenon=warning_data.get('phenomenon', '')
                )
                warnings.append(warning)

            return warnings

        except Exception as e:
            logger.error(f"Erro ao obter avisos meteorológicos: {e}")
            return []

    def _get_warning_level(self, level_id: int) -> str:
        """Mapeia ID do nível de aviso para texto"""
        levels = {1: "verde", 2: "amarelo", 3: "laranja", 4: "vermelho"}
        return levels.get(level_id, "desconhecido")

    @lru_cache(maxsize=32, typed=True)
    def get_seismic_data(self, region: str = "continente") -> List[SeismicData]:
        """Obtém dados sísmicos dos últimos 30 dias"""
        try:
            endpoints = {
                "continente": f"{self.BASE_URL}/earthquake/hp2.json",
                "acores": f"{self.BASE_URL}/earthquake/hp2-azores.json",
                "madeira": f"{self.BASE_URL}/earthquake/hp2-madeira.json"
            }

            url = endpoints.get(region.lower(), endpoints["continente"])
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()
            seismic_events = []

            for event in data.get('data', []):
                seismic_event = SeismicData(
                    id=str(event.get('id', '')),
                    magnitude=float(event.get('magnitude', 0)),
                    depth=float(event.get('depth', 0)),
                    location=event.get('location', ''),
                    time=event.get('time', ''),
                    coordinates={
                        "latitude": float(event.get('lat', 0)),
                        "longitude": float(event.get('lon', 0))
                    },
                    intensity=event.get('intensityID', None)
                )
                seismic_events.append(seismic_event)

            return seismic_events

        except Exception as e:
            logger.error(f"Erro ao obter dados sísmicos: {e}")
            return []

    @lru_cache(maxsize=32, typed=True)
    def get_sea_state(self, days: int = 3) -> List[SeaState]:
        """Obtém previsão do estado do mar até 3 dias"""
        try:
            response = self.session.get(f"{self.BASE_URL}/sea-conditions/hp-daily-sea-conditions-forecast.json")
            response.raise_for_status()

            data = response.json()
            sea_states = []

            for forecast in data.get('data', []):
                sea_state = SeaState(
                    date=forecast.get('forecastDate', ''),
                    location=forecast.get('location', ''),
                    wave_height=forecast.get('significantWaveHeight'),
                    wave_period=forecast.get('wavePeriod'),
                    wave_direction=forecast.get('waveDirection'),
                    sea_temperature=forecast.get('seaTemperature'),
                    coastal_conditions=forecast.get('coastalConditions')
                )
                sea_states.append(sea_state)

            return sea_states

        except Exception as e:
            logger.error(f"Erro ao obter estado do mar: {e}")
            return []

    @lru_cache(maxsize=64, typed=True)
    def get_fire_risk(self, days: int = 2) -> List[FireRisk]:
        """Obtém previsão do risco de incêndio até 2 dias"""
        try:
            response = self.session.get(f"{self.BASE_URL}/fire-risk/hp-daily-fire-risk-forecast.json")
            response.raise_for_status()

            data = response.json()
            fire_risks = []

            for risk_data in data.get('data', []):
                fire_risk = FireRisk(
                    date=risk_data.get('forecastDate', ''),
                    location=risk_data.get('local', ''),
                    risk_level=int(risk_data.get('riscoIncendio', 1)),
                    risk_description=self._get_fire_risk_description(risk_data.get('riscoIncendio', 1)),
                    temperature=risk_data.get('temperatura'),
                    humidity=risk_data.get('humidade'),
                    wind_speed=risk_data.get('vento')
                )
                fire_risks.append(fire_risk)

            return fire_risks

        except Exception as e:
            logger.error(f"Erro ao obter risco de incêndio: {e}")
            return []

    def _get_fire_risk_description(self, level: int) -> str:
        """Mapeia nível de risco de incêndio para descrição"""
        descriptions = {
            1: "Baixo", 2: "Moderado", 3: "Elevado", 4: "Muito Elevado", 5: "Máximo"
        }
        return descriptions.get(level, "Desconhecido")

    @lru_cache(maxsize=64, typed=True)
    def get_uv_index(self, days: int = 3) -> List[UVIndex]:
        """Obtém previsão do índice UV até 3 dias"""
        try:
            response = self.session.get(f"{self.BASE_URL}/uv/hp-daily-uv-index-forecast.json")
            response.raise_for_status()

            data = response.json()
            uv_indices = []

            for uv_data in data.get('data', []):
                uv_value = int(uv_data.get('iuv', 0))
                uv_index = UVIndex(
                    date=uv_data.get('forecastDate', ''),
                    location=uv_data.get('local', ''),
                    uv_index=uv_value,
                    uv_level=self._get_uv_level(uv_value),
                    protection_time=self._get_protection_time(uv_value)
                )
                uv_indices.append(uv_index)

            return uv_indices

        except Exception as e:
            logger.error(f"Erro ao obter índice UV: {e}")
            return []

    def _get_uv_level(self, uv_index: int) -> str:
        """Mapeia índice UV para nível de risco"""
        if uv_index <= 2:
            return "Baixo"
        elif uv_index <= 5:
            return "Moderado"
        elif uv_index <= 7:
            return "Alto"
        elif uv_index <= 10:
            return "Muito Alto"
        else:
            return "Extremo"

    def _get_protection_time(self, uv_index: int) -> int:
        """Estima tempo de proteção em minutos baseado no índice UV"""
        protection_times = {
            1: 60, 2: 45, 3: 30, 4: 25, 5: 20,
            6: 15, 7: 12, 8: 10, 9: 8, 10: 6, 11: 5
        }
        return protection_times.get(min(uv_index, 11), 5)

    @lru_cache(maxsize=32, typed=True)
    def get_weather_stations(self) -> List[WeatherStation]:
        """Obtém lista de estações meteorológicas"""
        try:
            response = self.session.get(f"{self.BASE_URL}/weather-stations.json")
            response.raise_for_status()

            data = response.json()
            stations = []

            for station_data in data.get('data', []):
                station = WeatherStation(
                    id=str(station_data.get('idEstacao', '')),
                    name=station_data.get('nome', ''),
                    coordinates={
                        "latitude": float(station_data.get('latitude', 0)),
                        "longitude": float(station_data.get('longitude', 0))
                    },
                    altitude=station_data.get('altitude')
                )
                stations.append(station)

            return stations

        except Exception as e:
            logger.error(f"Erro ao obter estações meteorológicas: {e}")
            return []

    def get_station_observations(self, station_id: str = None) -> List[StationObservation]:
        """Obtém observações meteorológicas das últimas 24 horas"""
        try:
            if station_id:
                url = f"{self.BASE_URL}/observation/meteorology/stations/observations.json"
                params = {"stationId": station_id}
                response = self.session.get(url, params=params)
            else:
                response = self.session.get(f"{self.BASE_URL}/observation/meteorology/stations/observations.json")

            response.raise_for_status()
            data = response.json()
            observations = []

            for obs_data in data.get('data', []):
                observation = StationObservation(
                    station_id=str(obs_data.get('idEstacao', '')),
                    station_name=obs_data.get('nomeEstacao', ''),
                    timestamp=obs_data.get('time', ''),
                    temperature=obs_data.get('temperatura'),
                    humidity=obs_data.get('humidade'),
                    pressure=obs_data.get('pressao'),
                    wind_speed=obs_data.get('intensidadeVento'),
                    wind_direction=obs_data.get('direcaoVento'),
                    precipitation=obs_data.get('precipitacao'),
                    visibility=obs_data.get('visibilidade')
                )
                observations.append(observation)

            return observations

        except Exception as e:
            logger.error(f"Erro ao obter observações de estações: {e}")
            return []

    def get_agricultural_data(self, data_type: str, municipality: str = None) -> List[AgriculturalData]:
        """Obtém dados agrícolas (evapotranspiração, precipitação, temperaturas, PDSI)"""
        try:
            endpoints = {
                "evapotranspiration": f"{self.BASE_URL}/climate/evapotranspiration",
                "precipitation": f"{self.BASE_URL}/climate/precipitation",
                "temperature_min": f"{self.BASE_URL}/climate/temperature-min",
                "temperature_max": f"{self.BASE_URL}/climate/temperature-max",
                "pdsi": f"{self.BASE_URL}/climate/pdsi"
            }

            if data_type not in endpoints:
                logger.error(f"Tipo de dados agrícolas inválido: {data_type}")
                return []

            response = self.session.get(endpoints[data_type])
            response.raise_for_status()

            # Processar CSV
            agricultural_data = []
            lines = response.text.strip().split('\n')

            if len(lines) < 2:
                return []

            headers = lines[0].split(',')
            for line in lines[1:]:
                values = line.split(',')
                if len(values) >= 3:
                    data_entry = AgriculturalData(
                        date=values[0] if len(values) > 0 else '',
                        municipality=values[1] if len(values) > 1 else '',
                        evapotranspiration=float(values[2]) if data_type == "evapotranspiration" and len(values) > 2 and values[2] else None,
                        precipitation=float(values[2]) if data_type == "precipitation" and len(values) > 2 and values[2] else None,
                        min_temperature=float(values[2]) if data_type == "temperature_min" and len(values) > 2 and values[2] else None,
                        max_temperature=float(values[2]) if data_type == "temperature_max" and len(values) > 2 and values[2] else None,
                        pdsi_index=float(values[2]) if data_type == "pdsi" and len(values) > 2 and values[2] else None
                    )

                    if municipality is None or data_entry.municipality.lower() == municipality.lower():
                        agricultural_data.append(data_entry)

            return agricultural_data

        except Exception as e:
            logger.error(f"Erro ao obter dados agrícolas: {e}")
            return []

    @lru_cache(maxsize=16, typed=True)
    def get_water_quality(self) -> List[WaterQuality]:
        """Obtém interdições à apanha nas zonas de produção de moluscos bivalves"""
        try:
            response = self.session.get(f"{self.BASE_URL}/sea-conditions/bivalve-mollusk-zones.json")
            response.raise_for_status()

            data = response.json()
            water_quality_data = []

            for zone_data in data.get('features', []):
                properties = zone_data.get('properties', {})
                geometry = zone_data.get('geometry', {})
                coordinates = geometry.get('coordinates', [])

                water_quality = WaterQuality(
                    zone_id=str(properties.get('id', '')),
                    zone_name=properties.get('nome', ''),
                    status=properties.get('estado', ''),
                    restriction_type=properties.get('tipo_restricao'),
                    coordinates={
                        "latitude": coordinates[1] if len(coordinates) >= 2 else 0,
                        "longitude": coordinates[0] if len(coordinates) >= 1 else 0
                    },
                    last_update=properties.get('data_atualizacao', '')
                )
                water_quality_data.append(water_quality)

            return water_quality_data

        except Exception as e:
            logger.error(f"Erro ao obter qualidade da água: {e}")
            return []

    # ==================== MÉTODOS AUXILIARES EXPANDIDOS ====================

    @lru_cache(maxsize=32, typed=True)
    def get_wind_intensity_classes(self) -> Dict[int, str]:
        """Obtém classes de intensidade do vento"""
        try:
            response = self.session.get(f"{self.BASE_URL}/wind-speed-daily-classe.json")
            response.raise_for_status()

            data = response.json()
            classes = {}

            for class_data in data.get('data', []):
                classes[class_data.get('idWindSpeedDailyClasse')] = class_data.get('descWindSpeedDailyClassePT', '')

            return classes

        except Exception as e:
            logger.error(f"Erro ao obter classes de intensidade do vento: {e}")
            return {}

    @lru_cache(maxsize=32, typed=True)
    def get_precipitation_classes(self) -> Dict[int, str]:
        """Obtém classes de precipitação"""
        try:
            response = self.session.get(f"{self.BASE_URL}/precipitation-type-classe.json")
            response.raise_for_status()

            data = response.json()
            classes = {}

            for class_data in data.get('data', []):
                classes[class_data.get('idPrecipitationTypeClasse')] = class_data.get('descPrecipitationTypeClassePT', '')

            return classes

        except Exception as e:
            logger.error(f"Erro ao obter classes de precipitação: {e}")
            return {}

    # ==================== MÉTODOS ORIGINAIS MANTIDOS ====================

    def find_location_id(self, district: str, location: str) -> Optional[int]:
        """Encontra o ID de uma localidade específica"""
        districts_locations = self.get_districts_and_locations()

        district_key = district.lower().strip()
        location_name = location.lower().strip()

        if district_key not in districts_locations:
            return None

        for loc in districts_locations[district_key]:
            if loc.name.lower().strip() == location_name:
                return loc.id

        return None

    def get_locations_by_district(self, district: str) -> List[Location]:
        """Obtém todas as localidades de um distrito"""
        districts_locations = self.get_districts_and_locations()
        district_key = district.lower().strip()

        return districts_locations.get(district_key, [])

    @lru_cache(maxsize=512, typed=True)
    def get_forecast(self, location_id: int, days: int = 5) -> Optional[Dict[str, Any]]:
        """Obtém previsão meteorológica para uma localidade com cache"""
        try:
            response = self.session.get(f"{self.BASE_URL}/forecast/meteorology/cities/daily/{location_id}.json")
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Erro ao obter previsão para localidade {location_id}: {e}")
            return None

    def parse_forecast_data(self, raw_data: Dict[str, Any], district: str, location: str, target_date: Optional[str] = None) -> Optional[DailyForecast]:
        """Converte dados brutos da API em modelo DailyForecast"""
        if not raw_data or 'data' not in raw_data:
            return None

        weather_conditions = self.get_weather_conditions()
        forecasts_data = raw_data['data']

        if target_date:
            target_date_str = target_date
        else:
            target_date_str = datetime.now().strftime('%Y-%m-%d')

        hourly_forecasts = []
        min_temp = float('inf')
        max_temp = float('-inf')

        for forecast in forecasts_data:
            forecast_date = forecast.get('forecastDate', '')

            if not forecast_date.startswith(target_date_str):
                continue

            try:
                if 'T' in forecast_date:
                    forecast_datetime = datetime.fromisoformat(forecast_date.replace('Z', '+00:00') if 'Z' in forecast_date else forecast_date)
                    hour = forecast_datetime.strftime('%H:%M')
                else:
                    hour = "12:00"
            except:
                hour = "12:00"

            temp = forecast.get('tMed') or forecast.get('tMax') or forecast.get('tMin')
            if temp is not None:
                temp = float(temp)
                min_temp = min(min_temp, temp)
                max_temp = max(max_temp, temp)

            weather_type_id = forecast.get('idWeatherType', 0)
            weather_desc = weather_conditions.get(weather_type_id, 'Desconhecido')

            weather_condition = WeatherCondition(
                id=weather_type_id,
                description=weather_desc
            )

            hourly_forecast = HourlyForecast(
                hour=hour,
                temperature=temp or 0.0,
                weather_condition=weather_condition,
                precipitation_probability=forecast.get('probabilityOfPrecipitation'),
                wind_speed=forecast.get('ffVento'),
                wind_direction=forecast.get('ddVento')
            )

            hourly_forecasts.append(hourly_forecast)

        if not hourly_forecasts:
            return None

        return DailyForecast(
            date=target_date_str,
            location=location,
            district=district,
            hourly_forecasts=hourly_forecasts,
            min_temperature=min_temp if min_temp != float('inf') else None,
            max_temperature=max_temp if max_temp != float('-inf') else None
        )

    def get_forecast_for_location(self, district: str, location: str, target_date: Optional[str] = None) -> Optional[DailyForecast]:
        """Obtém previsão para uma localidade específica"""
        location_id = self.find_location_id(district, location)

        if not location_id:
            return None

        raw_data = self.get_forecast(location_id)

        if not raw_data:
            return None

        return self.parse_forecast_data(raw_data, district, location, target_date)
