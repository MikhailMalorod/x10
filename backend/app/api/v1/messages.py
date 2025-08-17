"""
API endpoints для работы с сообщениями консилиума
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.messages import Message, MessageThread, MessageType, MessageRole
from app.services.messages import message_service

router = APIRouter()

@router.get("/meetings/{meeting_id}/messages", response_model=List[Message])
async def get_messages(
    meeting_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    message_type: Optional[MessageType] = None
) -> List[Message]:
    """Получает список сообщений встречи с пагинацией"""
    offset = (page - 1) * size
    return message_service.get_messages(
        meeting_id=meeting_id,
        limit=size,
        offset=offset,
        message_type=message_type
    )

@router.get("/messages/{message_id}", response_model=Message)
async def get_message(message_id: str) -> Message:
    """Получает сообщение по ID"""
    message = message_service.get_message(message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сообщение {message_id} не найдено"
        )
    return message

@router.post("/meetings/{meeting_id}/messages", response_model=Message)
async def create_message(
    meeting_id: str,
    content: str,
    run_id: str,
    agent_id: str,
    role: MessageRole = MessageRole.USER,
    reply_to: Optional[str] = None,
    thread_id: Optional[str] = None
) -> Message:
    """Создает новое сообщение в встрече"""
    return message_service.create_message(
        meeting_id=meeting_id,
        run_id=run_id,
        agent_id=agent_id,
        role=role,
        content=content,
        reply_to=reply_to,
        thread_id=thread_id
    )

@router.get("/meetings/{meeting_id}/threads", response_model=List[MessageThread])
async def get_threads(meeting_id: str) -> List[MessageThread]:
    """Получает все цепочки сообщений встречи"""
    return message_service.get_threads(meeting_id)

@router.get("/threads/{thread_id}", response_model=MessageThread)
async def get_thread(thread_id: str) -> MessageThread:
    """Получает цепочку сообщений по ID"""
    thread = message_service.get_thread(thread_id)
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Цепочка {thread_id} не найдена"
        )
    return thread

@router.post("/meetings/{meeting_id}/threads", response_model=MessageThread)
async def create_thread(
    meeting_id: str,
    metadata: Optional[dict] = None
) -> MessageThread:
    """Создает новую цепочку сообщений"""
    return message_service.create_thread(
        meeting_id=meeting_id,
        metadata=metadata
    ) 