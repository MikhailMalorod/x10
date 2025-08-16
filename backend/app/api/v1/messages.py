"""
Messages API endpoints для XIO
"""

from fastapi import APIRouter, status, Query
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/meetings/{meeting_id}/messages", status_code=status.HTTP_200_OK)
async def get_messages(
    meeting_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100)
) -> Dict[str, Any]:
    """Получить сообщения встречи с пагинацией"""
    # TODO: Получение из БД с пагинацией
    
    return {
        "meeting_id": meeting_id,
        "page": page,
        "size": size,
        "total": 10,
        "messages": [
            {
                "id": "msg_001",
                "agent_id": "moderator",
                "role": "assistant",
                "content": "Добро пожаловать на консилиум экспертов!",
                "created_at": "2024-01-01T00:00:00Z",
                "tool_call_thread_id": None
            },
            {
                "id": "msg_002",
                "agent_id": "expert_1",
                "role": "assistant", 
                "content": "Рассмотрим следующие альтернативы...",
                "created_at": "2024-01-01T00:01:00Z",
                "tool_call_thread_id": None
            }
        ]
    }


@router.post("/meetings/{meeting_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_user_message(meeting_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Добавить пользовательское сообщение/вопрос"""
    # TODO: Валидация и сохранение в БД
    # TODO: Уведомление оркестратора о новом сообщении
    
    message_id = "msg_user_001"  # Заглушка
    
    return {
        "id": message_id,
        "meeting_id": meeting_id,
        "role": "user",
        "content": message_data.get("content"),
        "created_at": "2024-01-01T00:02:00Z"
    } 