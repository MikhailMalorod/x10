"""
Artifacts API endpoints для XIO
"""

from fastapi import APIRouter, status
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/meetings/{meeting_id}/artifacts", status_code=status.HTTP_200_OK)
async def get_artifacts(meeting_id: str) -> List[Dict[str, Any]]:
    """Получить артефакты встречи"""
    # TODO: Получение из БД
    
    return [
        {
            "id": "artifact_001",
            "meeting_id": meeting_id,
            "type": "decision_log",
            "title": "Решение по архитектуре микросервисов",
            "url": "https://notion.so/page123",
            "external_ref": "notion:page123",
            "summary": "Принято решение использовать event-driven архитектуру",
            "created_at": "2024-01-01T00:05:00Z"
        },
        {
            "id": "artifact_002",
            "meeting_id": meeting_id,
            "type": "action_item",
            "title": "Создать диаграмму архитектуры",
            "url": "https://notion.so/task456",
            "external_ref": "notion:task456",
            "summary": "Задача назначена на команду архитектуры",
            "created_at": "2024-01-01T00:06:00Z"
        }
    ]


@router.get("/artifacts/{artifact_id}", status_code=status.HTTP_200_OK)
async def get_artifact(artifact_id: str) -> Dict[str, Any]:
    """Получить конкретный артефакт"""
    # TODO: Получение из БД
    
    return {
        "id": artifact_id,
        "meeting_id": "meeting_123",
        "type": "decision_log",
        "title": "Решение по архитектуре микросервисов",
        "content": {
            "alternatives": [
                "Монолитная архитектура",
                "Микросервисы с событиями",
                "Модульный монолит"
            ],
            "rationale": "Микросервисы обеспечивают лучшую масштабируемость",
            "risks": ["Сложность управления", "Сетевая задержка"],
            "decision": "Использовать event-driven микросервисы"
        },
        "url": "https://notion.so/page123",
        "created_at": "2024-01-01T00:05:00Z"
    } 