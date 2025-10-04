from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.ipma_service import IPMAService
from app.models import StationsResponse, ObservationsResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stations", tags=["stations"])
ipma_service = IPMAService()


@router.get("/", response_model=StationsResponse)
async def get_weather_stations():
    """
    Obtém lista de todas as estações meteorológicas

    Returns:
        Lista de estações meteorológicas com coordenadas
    """
    try:
        stations = ipma_service.get_weather_stations()

        if not stations:
            return StationsResponse(
                success=True,
                data=[],
                message="Nenhuma estação meteorológica encontrada"
            )

        return StationsResponse(
            success=True,
            data=stations,
            message=f"Estações meteorológicas encontradas: {len(stations)}"
        )

    except Exception as e:
        logger.error(f"Erro ao obter estações meteorológicas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/observations", response_model=ObservationsResponse)
async def get_station_observations(station_id: Optional[str] = Query(None, description="ID da estação específica")):
    """
    Obtém observações meteorológicas das últimas 24 horas

    Args:
        station_id: ID da estação específica (opcional)

    Returns:
        Observações meteorológicas das estações
    """
    try:
        observations = ipma_service.get_station_observations(station_id)

        if not observations:
            message = f"Nenhuma observação encontrada para a estação {station_id}" if station_id else "Nenhuma observação meteorológica disponível"
            return ObservationsResponse(
                success=True,
                data=[],
                message=message
            )

        return ObservationsResponse(
            success=True,
            data=observations,
            message=f"Observações encontradas: {len(observations)}"
        )

    except Exception as e:
        logger.error(f"Erro ao obter observações meteorológicas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/observations/latest")
async def get_latest_observations():
    """
    Obtém as observações mais recentes de todas as estações (últimas 3 horas)

    Returns:
        Observações meteorológicas mais recentes em formato otimizado
    """
    try:
        # Este endpoint usa dados das últimas 3 horas em formato GeoJSON
        observations = ipma_service.get_station_observations()

        # Filtrar apenas as observações mais recentes
        if observations:
            # Ordenar por timestamp e pegar as mais recentes
            sorted_obs = sorted(observations, key=lambda x: x.timestamp, reverse=True)
            latest_obs = sorted_obs[:50]  # Top 50 mais recentes

            return ObservationsResponse(
                success=True,
                data=latest_obs,
                message=f"Observações mais recentes: {len(latest_obs)}"
            )
        else:
            return ObservationsResponse(
                success=True,
                data=[],
                message="Nenhuma observação recente disponível"
            )

    except Exception as e:
        logger.error(f"Erro ao obter observações mais recentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
