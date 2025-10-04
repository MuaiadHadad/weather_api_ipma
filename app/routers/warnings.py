from fastapi import APIRouter, HTTPException
from typing import List
from app.services.ipma_service import IPMAService
from app.models import WeatherWarningsResponse, WeatherWarning
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/warnings", tags=["warnings"])
ipma_service = IPMAService()


@router.get("/", response_model=WeatherWarningsResponse)
async def get_weather_warnings():
    """
    Obtém avisos meteorológicos até 3 dias

    Returns:
        Lista de avisos meteorológicos ativos
    """
    try:
        warnings = ipma_service.get_weather_warnings()

        if not warnings:
            return WeatherWarningsResponse(
                success=True,
                data=[],
                message="Nenhum aviso meteorológico ativo no momento"
            )

        return WeatherWarningsResponse(success=True, data=warnings)

    except Exception as e:
        logger.error(f"Erro ao obter avisos meteorológicos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/by-level/{level}")
async def get_warnings_by_level(level: str):
    """
    Obtém avisos meteorológicos por nível de severidade

    Args:
        level: Nível do aviso (verde, amarelo, laranja, vermelho)

    Returns:
        Lista de avisos do nível especificado
    """
    try:
        all_warnings = ipma_service.get_weather_warnings()
        filtered_warnings = [w for w in all_warnings if w.level.lower() == level.lower()]

        return WeatherWarningsResponse(
            success=True,
            data=filtered_warnings,
            message=f"Avisos de nível {level}: {len(filtered_warnings)} encontrados"
        )

    except Exception as e:
        logger.error(f"Erro ao obter avisos por nível {level}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
