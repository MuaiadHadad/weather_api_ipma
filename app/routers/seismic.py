from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.ipma_service import IPMAService
from app.models import SeismicResponse, SeismicData
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seismic", tags=["seismic"])
ipma_service = IPMAService()


@router.get("/", response_model=SeismicResponse)
async def get_seismic_data(region: str = Query("continente", description="Região: continente, acores, madeira")):
    """
    Obtém dados sísmicos dos últimos 30 dias

    Args:
        region: Região para consulta (continente, acores, madeira)

    Returns:
        Lista de eventos sísmicos
    """
    try:
        seismic_events = ipma_service.get_seismic_data(region)

        if not seismic_events:
            return SeismicResponse(
                success=True,
                data=[],
                message=f"Nenhum evento sísmico registado na região {region}"
            )

        return SeismicResponse(
            success=True,
            data=seismic_events,
            message=f"Eventos sísmicos encontrados: {len(seismic_events)}"
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados sísmicos para {region}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/magnitude/{min_magnitude}")
async def get_seismic_by_magnitude(
    min_magnitude: float,
    region: str = Query("continente", description="Região: continente, acores, madeira")
):
    """
    Obtém eventos sísmicos acima de uma magnitude mínima

    Args:
        min_magnitude: Magnitude mínima dos eventos
        region: Região para consulta

    Returns:
        Lista de eventos sísmicos filtrados por magnitude
    """
    try:
        all_events = ipma_service.get_seismic_data(region)
        filtered_events = [event for event in all_events if event.magnitude >= min_magnitude]

        return SeismicResponse(
            success=True,
            data=filtered_events,
            message=f"Eventos com magnitude >= {min_magnitude}: {len(filtered_events)}"
        )

    except Exception as e:
        logger.error(f"Erro ao filtrar eventos sísmicos por magnitude: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
