"""
Health check endpoints для XIO
"""

from fastapi import APIRouter, status
from typing import Dict, Any
import logging

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Базовая проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "XIO Backend",
        "version": "0.1.0"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Проверка готовности сервиса к обработке запросов"""
    settings = get_settings()
    
    # TODO: Добавить проверки подключений к БД, Redis, ChromaDB
    checks = {
        "database": "unknown",  # await check_database_connection()
        "redis": "unknown",     # await check_redis_connection()
        "chroma": "unknown",    # await check_chroma_connection()
    }
    
    all_ready = all(check == "healthy" for check in checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "service": "XIO Backend",
        "version": "0.1.0",
        "checks": checks
    }


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def metrics() -> Dict[str, Any]:
    """Базовые метрики сервиса"""
    # TODO: Интеграция с Prometheus
    return {
        "active_meetings": 0,
        "total_runs": 0,
        "active_runs": 0,
        "tool_calls_total": 0
    } 