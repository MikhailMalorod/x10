"""
Модели для участников консилиума
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ParticipantRole(str, Enum):
    """Роль участника в консилиуме"""
    MODERATOR = "moderator"  # Ведущий консилиума
    EXPERT = "expert"  # Эксперт по предметной области
    SCRIBE = "scribe"  # Хронист для фиксации решений
    INTEGRATOR = "integrator"  # Интегратор для создания задач
    USER = "user"  # Пользователь-наблюдатель

class ParticipantStatus(str, Enum):
    """Статус участника в консилиуме"""
    SPEAKING = "speaking"  # Сейчас говорит
    NEXT = "next"  # Следующий в очереди
    WAITING = "waiting"  # Ожидает своей очереди
    BUSY = "busy"  # Занят (например, вызывает инструмент)
    INACTIVE = "inactive"  # Неактивен

class ToolBadge(BaseModel):
    """Значок доступного инструмента"""
    tool_id: str = Field(..., description="Идентификатор инструмента")
    name: str = Field(..., description="Название инструмента")
    icon: Optional[str] = Field(None, description="Иконка инструмента")
    description: Optional[str] = Field(None, description="Описание инструмента")

class Participant(BaseModel):
    """Участник консилиума"""
    agent_id: str = Field(..., description="Уникальный идентификатор агента")
    meeting_id: str = Field(..., description="Идентификатор встречи")
    role: ParticipantRole = Field(..., description="Роль участника")
    name: str = Field(..., description="Отображаемое имя")
    status: ParticipantStatus = Field(default=ParticipantStatus.WAITING, description="Текущий статус")
    model: Optional[str] = Field(None, description="Используемая модель (для LLM)")
    tool_badges: List[ToolBadge] = Field(default_factory=list, description="Доступные инструменты")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "moderator_1",
                "meeting_id": "meet_123",
                "role": "moderator",
                "name": "Модератор",
                "status": "speaking",
                "model": "gpt-4",
                "tool_badges": [
                    {
                        "tool_id": "notion.decision_log",
                        "name": "Notion Decision Log",
                        "icon": "📝",
                        "description": "Создание страницы с решением"
                    }
                ],
                "metadata": {
                    "speaking_order": 1,
                    "specialization": "Архитектура"
                }
            }
        }

class ParticipantUpdate(BaseModel):
    """Обновление статуса участника"""
    status: ParticipantStatus = Field(..., description="Новый статус")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Обновление метаданных")

class SpeakingOrder(BaseModel):
    """Порядок выступления участников"""
    meeting_id: str = Field(..., description="Идентификатор встречи")
    current_speaker: Optional[str] = Field(None, description="ID текущего спикера")
    next_speaker: Optional[str] = Field(None, description="ID следующего спикера")
    order: List[str] = Field(..., description="Порядок выступления (список agent_id)")
    round: int = Field(default=1, description="Текущий раунд обсуждения")

    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": "meet_123",
                "current_speaker": "moderator_1",
                "next_speaker": "expert_1",
                "order": ["moderator_1", "expert_1", "expert_2", "scribe_1"],
                "round": 1
            }
        } 