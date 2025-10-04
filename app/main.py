from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import forecast, warnings, seismic, marine, stations, agriculture
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Criar instância da aplicação FastAPI
app = FastAPI(
    title="Weather API IPMA - Completa",
    description="""
    API COMPLETA para todos os recursos do IPMA (Instituto Português do Mar e da Atmosfera)
    
    ## 🌤️ Recursos Disponíveis:
    
    ### Previsões Meteorológicas
    - Previsão diária até 5 dias por localidade
    - Previsão por data específica
    - Lista de distritos e localidades
    
    ### ⚠️ Avisos Meteorológicos
    - Avisos até 3 dias (verde, amarelo, laranja, vermelho)
    - Filtragem por nível de severidade
    
    ### 🌊 Dados Marítimos
    - Estado do mar até 3 dias
    - Risco de incêndio até 2 dias
    - Índice ultravioleta até 3 dias
    
    ### 🏠 Dados Sísmicos
    - Eventos sísmicos últimos 30 dias
    - Cobertura: Continente, Açores, Madeira
    - Filtragem por magnitude
    
    ### 🏭 Estações Meteorológicas
    - Lista de todas as estações
    - Observações das últimas 24 horas
    - Dados em tempo real
    
    ### 🌾 Dados Agrícolas
    - Evapotranspiração por concelho
    - Precipitação por concelho
    - Temperaturas min/max por concelho
    - Índice PDSI (seca)
    - Qualidade da água (moluscos bivalves)
    
    Todos os dados são obtidos diretamente da API oficial do IPMA com cache inteligente.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todos os routers
app.include_router(forecast.router)      # Previsões meteorológicas
app.include_router(warnings.router)     # Avisos meteorológicos
app.include_router(seismic.router)      # Dados sísmicos
app.include_router(marine.router)       # Dados marítimos (mar, incêndio, UV)
app.include_router(stations.router)     # Estações meteorológicas
app.include_router(agriculture.router)  # Dados agrícolas e qualidade água


@app.get("/")
async def root():
    """Endpoint raiz com informações completas da API"""
    return {
        "message": "Weather API IPMA - Versão Completa",
        "version": "2.0.0",
        "description": "API completa para TODOS os recursos do IPMA",
        "resources": {
            "meteorology": {
                "current_forecast": "/forecast/{distrito}/{localidade}",
                "forecast_by_date": "/forecast/{distrito}/{localidade}/?day=YYYY-MM-DD",
                "locations": "/forecast/{distrito}",
                "districts": "/forecast/"
            },
            "warnings": {
                "all_warnings": "/warnings/",
                "by_level": "/warnings/by-level/{level}"
            },
            "seismic": {
                "all_events": "/seismic/?region=continente|acores|madeira",
                "by_magnitude": "/seismic/magnitude/{min_magnitude}"
            },
            "marine": {
                "sea_state": "/marine/sea-state",
                "fire_risk": "/marine/fire-risk",
                "fire_risk_level": "/marine/fire-risk/level/{min_level}",
                "uv_index": "/marine/uv-index",
                "uv_by_level": "/marine/uv-index/level/{level}"
            },
            "stations": {
                "all_stations": "/stations/",
                "observations": "/stations/observations",
                "specific_station": "/stations/observations?station_id={id}",
                "latest": "/stations/observations/latest"
            },
            "agriculture": {
                "evapotranspiration": "/agriculture/evapotranspiration",
                "precipitation": "/agriculture/precipitation",
                "temperature_min": "/agriculture/temperature-min",
                "temperature_max": "/agriculture/temperature-max",
                "drought_index": "/agriculture/pdsi",
                "water_quality": "/agriculture/water-quality",
                "water_by_status": "/agriculture/water-quality/status/{status}"
            }
        },
        "examples": {
            "basic_forecast": "/forecast/lisboa/lisboa",
            "forecast_with_date": "/forecast/porto/porto/?day=2025-10-08",
            "weather_warnings": "/warnings/",
            "seismic_events": "/seismic/?region=continente",
            "fire_risk": "/marine/fire-risk",
            "uv_index": "/marine/uv-index",
            "weather_stations": "/stations/",
            "agricultural_data": "/agriculture/precipitation"
        },
        "total_endpoints": "25+ endpoints",
        "data_sources": [
            "Previsões meteorológicas até 5 dias",
            "Avisos meteorológicos até 3 dias",
            "Dados sísmicos últimos 30 dias",
            "Estado do mar até 3 dias",
            "Risco de incêndio até 2 dias",
            "Índice UV até 3 dias",
            "Observações estações 24h",
            "Dados agrícolas por concelho",
            "Qualidade da água costeira"
        ]
    }


@app.get("/dashboard")
async def dashboard():
    """
    Dashboard completo com resumo de todos os dados disponíveis

    Returns:
        Resumo executivo de todos os recursos da API
    """
    try:
        from app.services.ipma_service import IPMAService
        ipma_service = IPMAService()

        # Obter contadores de dados disponíveis
        districts_count = len(ipma_service.get_districts_and_locations())
        warnings_count = len(ipma_service.get_weather_warnings())
        seismic_count = len(ipma_service.get_seismic_data())
        stations_count = len(ipma_service.get_weather_stations())

        return {
            "success": True,
            "dashboard": {
                "api_status": "🟢 Online",
                "version": "2.0.0",
                "last_update": "2025-10-04",
                "data_summary": {
                    "districts_available": districts_count,
                    "active_warnings": warnings_count,
                    "recent_seismic_events": seismic_count,
                    "weather_stations": stations_count
                },
                "service_status": {
                    "meteorology": "🟢 Ativo",
                    "warnings": "🟢 Ativo",
                    "seismic": "🟢 Ativo",
                    "marine": "🟢 Ativo",
                    "stations": "🟢 Ativo",
                    "agriculture": "🟢 Ativo"
                },
                "coverage": {
                    "portugal_mainland": "✅ Completa",
                    "azores": "✅ Completa",
                    "madeira": "✅ Completa",
                    "marine_areas": "✅ Completa"
                },
                "data_freshness": {
                    "forecasts": "Atualizadas 4x/dia",
                    "warnings": "Tempo real",
                    "seismic": "Últimos 30 dias",
                    "observations": "Últimas 24 horas",
                    "agriculture": "Dados diários"
                }
            },
            "quick_links": {
                "documentation": "/docs",
                "all_endpoints": "/",
                "health_check": "/health"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao gerar dashboard: {e}",
            "fallback_info": "Use /docs para documentação completa"
        }


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API expandida"""
    try:
        from app.services.ipma_service import IPMAService
        ipma_service = IPMAService()

        # Teste rápido de conectividade
        test_districts = ipma_service.get_districts_and_locations()

        return {
            "status": "healthy",
            "message": "API IPMA Completa funcionando",
            "version": "2.0.0",
            "services": {
                "ipma_connection": "✅ OK" if test_districts else "❌ Erro",
                "total_endpoints": "25+",
                "cache_status": "✅ Ativo"
            },
            "timestamp": "2025-10-04T12:00:00Z"
        }

    except Exception as e:
        return {
            "status": "degraded",
            "message": f"API com problemas: {e}",
            "version": "2.0.0"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
