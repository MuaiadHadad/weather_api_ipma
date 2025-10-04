from fastapi import APIRouter, HTTPException
from app.services.ipma_service import IPMAService
from app.models import SeaStateResponse, FireRiskResponse, UVIndexResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marine", tags=["marine"])
ipma_service = IPMAService()


@router.get("/sea-state", response_model=SeaStateResponse)
async def get_sea_state():
    """
    Obtém previsão do estado do mar até 3 dias

    Returns:
        Previsões das condições marítimas
    """
    try:
        sea_conditions = ipma_service.get_sea_state()

        if not sea_conditions:
            return SeaStateResponse(
                success=True,
                data=[],
                message="Dados do estado do mar indisponíveis"
            )

        return SeaStateResponse(success=True, data=sea_conditions)

    except Exception as e:
        logger.error(f"Erro ao obter estado do mar: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/fire-risk", response_model=FireRiskResponse)
async def get_fire_risk():
    """
    Obtém previsão do risco de incêndio até 2 dias

    Returns:
        Previsões do risco de incêndio por localidade
    """
    try:
        fire_risks = ipma_service.get_fire_risk()

        if not fire_risks:
            return FireRiskResponse(
                success=True,
                data=[],
                message="Dados de risco de incêndio indisponíveis"
            )

        return FireRiskResponse(success=True, data=fire_risks)

    except Exception as e:
        logger.error(f"Erro ao obter risco de incêndio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/fire-risk/level/{min_level}")
async def get_fire_risk_by_level(min_level: int):
    """
    Obtém localidades com risco de incêndio acima de um nível mínimo

    Args:
        min_level: Nível mínimo de risco (1-5)

    Returns:
        Localidades com risco igual ou superior ao especificado
    """
    try:
        if min_level < 1 or min_level > 5:
            raise HTTPException(status_code=400, detail="Nível deve estar entre 1 e 5")

        all_risks = ipma_service.get_fire_risk()
        filtered_risks = [risk for risk in all_risks if risk.risk_level >= min_level]

        return FireRiskResponse(
            success=True,
            data=filtered_risks,
            message=f"Localidades com risco >= {min_level}: {len(filtered_risks)}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao filtrar risco de incêndio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/uv-index", response_model=UVIndexResponse)
async def get_uv_index():
    """
    Obtém previsão do índice UV até 3 dias

    Returns:
        Índices ultravioleta por localidade
    """
    try:
        uv_data = ipma_service.get_uv_index()

        if not uv_data:
            return UVIndexResponse(
                success=True,
                data=[],
                message="Dados de índice UV indisponíveis"
            )

        return UVIndexResponse(success=True, data=uv_data)

    except Exception as e:
        logger.error(f"Erro ao obter índice UV: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/uv-index/level/{level}")
async def get_uv_by_level(level: str):
    """
    Obtém localidades com determinado nível de índice UV

    Args:
        level: Nível UV (baixo, moderado, alto, muito_alto, extremo)

    Returns:
        Localidades com o nível UV especificado
    """
    try:
        level_map = {
            "baixo": "Baixo",
            "moderado": "Moderado",
            "alto": "Alto",
            "muito_alto": "Muito Alto",
            "extremo": "Extremo"
        }

        if level.lower() not in level_map:
            raise HTTPException(
                status_code=400,
                detail="Nível deve ser: baixo, moderado, alto, muito_alto, extremo"
            )

        all_uv = ipma_service.get_uv_index()
        filtered_uv = [uv for uv in all_uv if uv.uv_level == level_map[level.lower()]]

        return UVIndexResponse(
            success=True,
            data=filtered_uv,
            message=f"Localidades com UV {level_map[level.lower()]}: {len(filtered_uv)}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao filtrar índice UV: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
