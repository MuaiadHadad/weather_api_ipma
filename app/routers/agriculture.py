from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.ipma_service import IPMAService
from app.models import AgriculturalResponse, WaterQualityResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agriculture", tags=["agriculture"])
ipma_service = IPMAService()


@router.get("/evapotranspiration", response_model=AgriculturalResponse)
async def get_evapotranspiration(municipality: Optional[str] = Query(None, description="Município específico")):
    """
    Obtém dados de evapotranspiração de referência diária por concelho

    Args:
        municipality: Nome do município (opcional)

    Returns:
        Dados de evapotranspiração em formato CSV processado
    """
    try:
        data = ipma_service.get_agricultural_data("evapotranspiration", municipality)

        if not data:
            message = f"Nenhum dado de evapotranspiração encontrado para {municipality}" if municipality else "Dados de evapotranspiração indisponíveis"
            return AgriculturalResponse(
                success=True,
                data=[],
                message=message
            )

        return AgriculturalResponse(
            success=True,
            data=data,
            message=f"Dados de evapotranspiração: {len(data)} registos"
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados de evapotranspiração: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/precipitation", response_model=AgriculturalResponse)
async def get_precipitation_data(municipality: Optional[str] = Query(None, description="Município específico")):
    """
    Obtém dados de precipitação total diária por concelho

    Args:
        municipality: Nome do município (opcional)

    Returns:
        Dados de precipitação em formato CSV processado
    """
    try:
        data = ipma_service.get_agricultural_data("precipitation", municipality)

        if not data:
            message = f"Nenhum dado de precipitação encontrado para {municipality}" if municipality else "Dados de precipitação indisponíveis"
            return AgriculturalResponse(
                success=True,
                data=[],
                message=message
            )

        return AgriculturalResponse(
            success=True,
            data=data,
            message=f"Dados de precipitação: {len(data)} registos"
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados de precipitação: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/temperature-min", response_model=AgriculturalResponse)
async def get_min_temperature(municipality: Optional[str] = Query(None, description="Município específico")):
    """
    Obtém dados de temperatura mínima diária por concelho

    Args:
        municipality: Nome do município (opcional)

    Returns:
        Dados de temperatura mínima em formato CSV processado
    """
    try:
        data = ipma_service.get_agricultural_data("temperature_min", municipality)

        if not data:
            message = f"Nenhum dado de temperatura mínima encontrado para {municipality}" if municipality else "Dados de temperatura mínima indisponíveis"
            return AgriculturalResponse(
                success=True,
                data=[],
                message=message
            )

        return AgriculturalResponse(
            success=True,
            data=data,
            message=f"Dados de temperatura mínima: {len(data)} registos"
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados de temperatura mínima: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/temperature-max", response_model=AgriculturalResponse)
async def get_max_temperature(municipality: Optional[str] = Query(None, description="Município específico")):
    """
    Obtém dados de temperatura máxima diária por concelho

    Args:
        municipality: Nome do município (opcional)

    Returns:
        Dados de temperatura máxima em formato CSV processado
    """
    try:
        data = ipma_service.get_agricultural_data("temperature_max", municipality)

        if not data:
            message = f"Nenhum dado de temperatura máxima encontrado para {municipality}" if municipality else "Dados de temperatura máxima indisponíveis"
            return AgriculturalResponse(
                success=True,
                data=[],
                message=message
            )

        return AgriculturalResponse(
            success=True,
            data=data,
            message=f"Dados de temperatura máxima: {len(data)} registos"
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados de temperatura máxima: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/pdsi", response_model=AgriculturalResponse)
async def get_pdsi_index(municipality: Optional[str] = Query(None, description="Município específico")):
    """
    Obtém índice PDSI (Palmer Drought Severity Index) mensal por concelho

    Args:
        municipality: Nome do município (opcional)

    Returns:
        Dados do índice PDSI que indica severidade da seca
    """
    try:
        data = ipma_service.get_agricultural_data("pdsi", municipality)

        if not data:
            message = f"Nenhum dado PDSI encontrado para {municipality}" if municipality else "Dados PDSI indisponíveis"
            return AgriculturalResponse(
                success=True,
                data=[],
                message=message
            )

        return AgriculturalResponse(
            success=True,
            data=data,
            message=f"Dados PDSI (índice de seca): {len(data)} registos"
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados PDSI: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/water-quality", response_model=WaterQualityResponse)
async def get_water_quality():
    """
    Obtém interdições à apanha nas zonas de produção de moluscos bivalves

    Returns:
        Estado das zonas de produção de moluscos (abertas/fechadas)
    """
    try:
        water_data = ipma_service.get_water_quality()

        if not water_data:
            return WaterQualityResponse(
                success=True,
                data=[],
                message="Dados de qualidade da água indisponíveis"
            )

        return WaterQualityResponse(
            success=True,
            data=water_data,
            message=f"Zonas de moluscos bivalves: {len(water_data)} registos"
        )

    except Exception as e:
        logger.error(f"Erro ao obter qualidade da água: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/water-quality/status/{status}")
async def get_water_quality_by_status(status: str):
    """
    Obtém zonas de moluscos bivalves por estado

    Args:
        status: Estado da zona (aberta, fechada, condicional)

    Returns:
        Zonas filtradas pelo estado especificado
    """
    try:
        all_zones = ipma_service.get_water_quality()
        filtered_zones = [zone for zone in all_zones if zone.status.lower() == status.lower()]

        return WaterQualityResponse(
            success=True,
            data=filtered_zones,
            message=f"Zonas com estado '{status}': {len(filtered_zones)}"
        )

    except Exception as e:
        logger.error(f"Erro ao filtrar qualidade da água por estado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
