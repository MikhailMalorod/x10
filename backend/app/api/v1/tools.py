"""
Tools API endpoints для XIO
"""

from fastapi import APIRouter, status
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tools/available", status_code=status.HTTP_200_OK)
async def get_available_tools() -> List[Dict[str, Any]]:
    """Получить список доступных инструментов"""
    # TODO: Получение из реестра
    
    return [
        {
            "definition_id": "notion.decision_log",
            "name": "Create Decision Log",
            "description": "Создает страницу с журналом решений в Notion",
            "visibility": "ce"
        },
        {
            "definition_id": "notion.action_item",
            "name": "Create Action Item",
            "description": "Создает задачу в Notion",
            "visibility": "ce"
        },
        {
            "definition_id": "slack.send_message",
            "name": "Send Slack Message",
            "description": "Отправляет сообщение в Slack",
            "visibility": "ce"
        }
    ]


@router.get("/tool-definitions", status_code=status.HTTP_200_OK)
async def list_tool_definitions() -> List[Dict[str, Any]]:
    """Получить список определений инструментов"""
    # TODO: Получение из БД
    
    return [
        {
            "definition_id": "notion.decision_log",
            "name": "Create Decision Log",
            "json_schema": {
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "string"},
                    "title": {"type": "string"},
                    "alternatives": {"type": "array"},
                    "rationale": {"type": "string"}
                },
                "required": ["meeting_id", "title"]
            },
            "runtime_constraints": {
                "timeout": 30,
                "cpu_limit": "0.1",
                "memory_limit": "128m"
            }
        }
    ]


@router.get("/tool-instances", status_code=status.HTTP_200_OK)
async def list_tool_instances() -> List[Dict[str, Any]]:
    """Получить список экземпляров инструментов"""
    # TODO: Получение из БД с учетом прав доступа
    
    return [
        {
            "instance_id": "notion_default",
            "definition_id": "notion.decision_log",
            "name": "Default Notion Integration",
            "scope": "global",
            "owner_id": "user_123"
        }
    ] 