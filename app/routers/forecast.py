from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.ipma_service import IPMAService
from app.models import ForecastResponse, LocationsResponse, DailyForecast, Location
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forecast", tags=["forecast"])
ipma_service = IPMAService()


@router.get("/{distrito}/{localidade}", response_model=ForecastResponse)
async def get_forecast_current(
    distrito: str,
    localidade: str
):
    """
    Obtém a previsão meteorológica atual para uma localidade específica

    Args:
        distrito: Nome do distrito (ex: "lisboa", "porto")
        localidade: Nome da localidade (ex: "lisboa", "cascais")

    Returns:
        Previsão meteorológica atual
    """
    try:
        forecast = ipma_service.get_forecast_for_location(distrito, localidade)

        if not forecast:
            # Verificar se o distrito existe
            locations = ipma_service.get_locations_by_district(distrito)
            if not locations:
                raise HTTPException(
                    status_code=404,
                    detail=f"Distrito '{distrito}' não encontrado"
                )

            # Verificar se a localidade existe no distrito
            location_names = [loc.name.lower() for loc in locations]
            if localidade.lower() not in location_names:
                raise HTTPException(
                    status_code=404,
                    detail=f"Localidade '{localidade}' não encontrada no distrito '{distrito}'. "
                           f"Localidades disponíveis: {', '.join([loc.name for loc in locations])}"
                )

            raise HTTPException(
                status_code=500,
                detail="Erro ao obter dados meteorológicos do IPMA"
            )

        return ForecastResponse(success=True, data=forecast)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter previsão para {distrito}/{localidade}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{distrito}/{localidade}/", response_model=ForecastResponse)
async def get_forecast_by_date(
    distrito: str,
    localidade: str,
    day: str = Query(..., description="Data no formato YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """
    Obtém a previsão meteorológica para uma data específica

    Args:
        distrito: Nome do distrito
        localidade: Nome da localidade
        day: Data da previsão no formato YYYY-MM-DD

    Returns:
        Previsão meteorológica para a data especificada
    """
    try:
        forecast = ipma_service.get_forecast_for_location(distrito, localidade, day)

        if not forecast:
            # Verificar se o distrito existe
            locations = ipma_service.get_locations_by_district(distrito)
            if not locations:
                raise HTTPException(
                    status_code=404,
                    detail=f"Distrito '{distrito}' não encontrado"
                )

            # Verificar se a localidade existe no distrito
            location_names = [loc.name.lower() for loc in locations]
            if localidade.lower() not in location_names:
                raise HTTPException(
                    status_code=404,
                    detail=f"Localidade '{localidade}' não encontrada no distrito '{distrito}'"
                )

            raise HTTPException(
                status_code=404,
                detail=f"Dados meteorológicos não disponíveis para {day}"
            )

        return ForecastResponse(success=True, data=forecast)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter previsão para {distrito}/{localidade} em {day}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{distrito}", response_model=LocationsResponse)
async def get_locations_by_district(distrito: str):
    """
    Obtém lista de localidades disponíveis para um distrito

    Args:
        distrito: Nome do distrito

    Returns:
        Lista de localidades do distrito
    """
    try:
        locations = ipma_service.get_locations_by_district(distrito)

        if not locations:
            raise HTTPException(
                status_code=404,
                detail=f"Distrito '{distrito}' não encontrado. "
                       "Verifique se o nome está correto (ex: 'lisboa', 'porto', 'faro')"
            )

        return LocationsResponse(success=True, data=locations)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter localidades do distrito {distrito}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/")
async def get_available_districts():
    """
    Obtém lista de todos os distritos disponíveis

    Returns:
        Lista de distritos disponíveis
    """
    try:
        districts_locations = ipma_service.get_districts_and_locations()
        districts = list(districts_locations.keys())

        return {
            "success": True,
            "data": {
                "districts": sorted(districts),
                "total": len(districts)
            },
            "message": "Para obter localidades de um distrito, use: GET /forecast/{distrito}"
        }

    except Exception as e:
        logger.error(f"Erro ao obter distritos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
