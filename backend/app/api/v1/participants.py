"""
Participants API endpoints для XIO
"""

from fastapi import APIRouter, status
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/meetings/{meeting_id}/participants", status_code=status.HTTP_200_OK)
async def get_participants(meeting_id: str) -> Dict[str, Any]:
    """Получить состав и статусы участников встречи"""
    # TODO: Получение из Redis/БД
    
    return {
        "meeting_id": meeting_id,
        "participants": [
            {
                "agent_id": "moderator",
                "role": "moderator",
                "name": "Модератор",
                "status": "speaking",
                "model": "gpt-4",
                "tool_badges": []
            },
            {
                "agent_id": "expert_1",
                "role": "expert",
                "name": "Эксперт по архитектуре",
                "status": "next",
                "model": "gpt-4",
                "tool_badges": []
            },
            {
                "agent_id": "expert_2",
                "role": "expert",
                "name": "Эксперт по безопасности",
                "status": "waiting",
                "model": "gpt-4",
                "tool_badges": []
            },
            {
                "agent_id": "scribe",
                "role": "scribe",
                "name": "Хронист",
                "status": "waiting",
                "model": "gpt-4",
                "tool_badges": []
            },
            {
                "agent_id": "integrator",
                "role": "integrator",
                "name": "Интегратор",
                "status": "waiting",
                "model": "gpt-4",
                "tool_badges": ["notion", "slack"]
            }
        ],
        "current_speaker": "moderator",
        "next_speaker": "expert_1",
        "speaking_order": ["moderator", "expert_1", "expert_2", "scribe", "integrator"]
    } 