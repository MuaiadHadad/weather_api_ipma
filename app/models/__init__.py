from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class WeatherCondition(BaseModel):
    """Modelo para condições meteorológicas"""
    id: int
    description: str


class HourlyForecast(BaseModel):
    """Modelo para previsão horária"""
    hour: str
    temperature: float
    weather_condition: WeatherCondition
    precipitation_probability: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None


class DailyForecast(BaseModel):
    """Modelo para previsão diária"""
    date: str
    location: str
    district: str
    hourly_forecasts: List[HourlyForecast]
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None


class Location(BaseModel):
    """Modelo para localidade"""
    id: int
    name: str
    district: str


# Novos modelos para recursos expandidos

class WeatherWarning(BaseModel):
    """Modelo para avisos meteorológicos"""
    id: str
    area: str
    warning_type: str
    level: str  # amarelo, laranja, vermelho
    start_time: str
    end_time: str
    description: str
    phenomenon: str


class SeismicData(BaseModel):
    """Modelo para dados sísmicos"""
    id: str
    magnitude: float
    depth: float
    location: str
    time: str
    coordinates: Dict[str, float]
    intensity: Optional[str] = None


class SeaState(BaseModel):
    """Modelo para estado do mar"""
    date: str
    location: str
    wave_height: Optional[float] = None
    wave_period: Optional[float] = None
    wave_direction: Optional[str] = None
    sea_temperature: Optional[float] = None
    coastal_conditions: Optional[str] = None


class FireRisk(BaseModel):
    """Modelo para risco de incêndio"""
    date: str
    location: str
    risk_level: int  # 1-5
    risk_description: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None


class UVIndex(BaseModel):
    """Modelo para índice ultravioleta"""
    date: str
    location: str
    uv_index: int
    uv_level: str  # baixo, moderado, alto, muito alto, extremo
    protection_time: Optional[int] = None  # minutos até queimadura


class WeatherStation(BaseModel):
    """Modelo para estação meteorológica"""
    id: str
    name: str
    coordinates: Dict[str, float]
    altitude: Optional[float] = None


class StationObservation(BaseModel):
    """Modelo para observação de estação"""
    station_id: str
    station_name: str
    timestamp: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    precipitation: Optional[float] = None
    visibility: Optional[float] = None


class AgriculturalData(BaseModel):
    """Modelo para dados agrícolas"""
    date: str
    municipality: str
    evapotranspiration: Optional[float] = None
    precipitation: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    pdsi_index: Optional[float] = None  # Palmer Drought Severity Index


class WaterQuality(BaseModel):
    """Modelo para qualidade da água (moluscos bivalves)"""
    zone_id: str
    zone_name: str
    status: str  # aberta, fechada, condicional
    restriction_type: Optional[str] = None
    coordinates: Dict[str, float]
    last_update: str


# Modelos de resposta expandidos

class WeatherWarningsResponse(BaseModel):
    """Resposta da API de avisos meteorológicos"""
    success: bool
    data: Optional[List[WeatherWarning]] = None
    message: Optional[str] = None


class SeismicResponse(BaseModel):
    """Resposta da API de dados sísmicos"""
    success: bool
    data: Optional[List[SeismicData]] = None
    message: Optional[str] = None


class SeaStateResponse(BaseModel):
    """Resposta da API de estado do mar"""
    success: bool
    data: Optional[List[SeaState]] = None
    message: Optional[str] = None


class FireRiskResponse(BaseModel):
    """Resposta da API de risco de incêndio"""
    success: bool
    data: Optional[List[FireRisk]] = None
    message: Optional[str] = None


class UVIndexResponse(BaseModel):
    """Resposta da API de índice UV"""
    success: bool
    data: Optional[List[UVIndex]] = None
    message: Optional[str] = None


class StationsResponse(BaseModel):
    """Resposta da API de estações"""
    success: bool
    data: Optional[List[WeatherStation]] = None
    message: Optional[str] = None


class ObservationsResponse(BaseModel):
    """Resposta da API de observações"""
    success: bool
    data: Optional[List[StationObservation]] = None
    message: Optional[str] = None


class AgriculturalResponse(BaseModel):
    """Resposta da API de dados agrícolas"""
    success: bool
    data: Optional[List[AgriculturalData]] = None
    message: Optional[str] = None


class WaterQualityResponse(BaseModel):
    """Resposta da API de qualidade da água"""
    success: bool
    data: Optional[List[WaterQuality]] = None
    message: Optional[str] = None


# Respostas originais
class ForecastResponse(BaseModel):
    """Resposta da API de previsão"""
    success: bool
    data: Optional[DailyForecast] = None
    message: Optional[str] = None


class LocationsResponse(BaseModel):
    """Resposta da API de localidades"""
    success: bool
    data: Optional[List[Location]] = None
    message: Optional[str] = None


class DistrictsResponse(BaseModel):
    """Resposta da API de distritos"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
