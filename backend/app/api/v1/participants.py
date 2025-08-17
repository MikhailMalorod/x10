"""
API endpoints для работы с участниками консилиума
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.models.participants import (
    Participant,
    ParticipantRole,
    ParticipantStatus,
    ToolBadge,
    ParticipantUpdate,
    SpeakingOrder
)
from app.services.participants import participant_service

router = APIRouter()

@router.get("/meetings/{meeting_id}/participants", response_model=List[Participant])
async def get_participants(meeting_id: str) -> List[Participant]:
    """Получает список участников встречи"""
    return participant_service.get_participants(meeting_id)

@router.get("/participants/{agent_id}", response_model=Participant)
async def get_participant(agent_id: str) -> Participant:
    """Получает участника по ID"""
    participant = participant_service.get_participant(agent_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Участник {agent_id} не найден"
        )
    return participant

@router.post("/meetings/{meeting_id}/participants", response_model=Participant)
async def create_participant(
    meeting_id: str,
    agent_id: str,
    role: ParticipantRole,
    name: str,
    model: Optional[str] = None,
    tool_badges: Optional[List[ToolBadge]] = None,
    metadata: Optional[dict] = None
) -> Participant:
    """Создает нового участника встречи"""
    return participant_service.create_participant(
        agent_id=agent_id,
        meeting_id=meeting_id,
        role=role,
        name=name,
        model=model,
        tool_badges=tool_badges,
        metadata=metadata
    )

@router.patch("/participants/{agent_id}", response_model=Participant)
async def update_participant_status(
    agent_id: str,
    update: ParticipantUpdate
) -> Participant:
    """Обновляет статус участника"""
    participant = participant_service.update_participant(agent_id, update)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Участник {agent_id} не найден"
        )
    return participant

@router.get("/meetings/{meeting_id}/speaking-order", response_model=SpeakingOrder)
async def get_speaking_order(meeting_id: str) -> SpeakingOrder:
    """Получает текущий порядок выступления"""
    order = participant_service.get_speaking_order(meeting_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Порядок выступления для встречи {meeting_id} не найден"
        )
    return order

@router.post("/meetings/{meeting_id}/speaking-order", response_model=SpeakingOrder)
async def create_speaking_order(meeting_id: str) -> SpeakingOrder:
    """Создает порядок выступления для встречи"""
    participants = participant_service.get_participants(meeting_id)
    if not participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Нет участников для встречи {meeting_id}"
        )
    return participant_service.create_speaking_order(meeting_id, participants)

@router.post("/meetings/{meeting_id}/next-speaker", response_model=SpeakingOrder)
async def next_speaker(meeting_id: str) -> SpeakingOrder:
    """Переключает на следующего спикера"""
    order = participant_service.next_speaker(meeting_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось переключить спикера для встречи {meeting_id}"
        )
    return order 