"""
Модели для сообщений консилиума
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    """Роль отправителя сообщения"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class MessageType(str, Enum):
    """Тип сообщения"""
    CHAT = "chat"  # Обычное сообщение
    DECISION = "decision"  # Принятие решения
    TASK = "task"  # Создание задачи
    TOOL_CALL = "tool_call"  # Вызов инструмента
    TOOL_RESULT = "tool_result"  # Результат инструмента
    STATUS = "status"  # Изменение статуса
    SUMMARY = "summary"  # Итоговое резюме

class Message(BaseModel):
    """Базовая модель сообщения"""
    id: str = Field(..., description="Уникальный идентификатор сообщения")
    meeting_id: str = Field(..., description="Идентификатор встречи")
    run_id: str = Field(..., description="Идентификатор запуска")
    agent_id: str = Field(..., description="Идентификатор агента")
    role: MessageRole = Field(..., description="Роль отправителя")
    type: MessageType = Field(default=MessageType.CHAT, description="Тип сообщения")
    content: str = Field(..., description="Текст сообщения")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания")
    reply_to: Optional[str] = Field(None, description="ID сообщения, на которое это является ответом")
    thread_id: Optional[str] = Field(None, description="ID цепочки сообщений")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_123",
                "meeting_id": "meet_123",
                "run_id": "run_123",
                "agent_id": "moderator",
                "role": "assistant",
                "type": "chat",
                "content": "Давайте обсудим варианты решения.",
                "created_at": "2024-01-20T10:00:00Z",
                "reply_to": None,
                "thread_id": None,
                "metadata": {}
            }
        }

class DecisionMessage(Message):
    """Сообщение о принятии решения"""
    type: Literal[MessageType.DECISION] = MessageType.DECISION
    metadata: Dict[str, Any] = Field(..., description="Метаданные решения")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_456",
                "meeting_id": "meet_123",
                "run_id": "run_123",
                "agent_id": "moderator",
                "role": "assistant",
                "type": "decision",
                "content": "Принято решение использовать микросервисную архитектуру.",
                "created_at": "2024-01-20T10:30:00Z",
                "metadata": {
                    "decision_id": "dec_123",
                    "alternatives_count": 3,
                    "selected_option": "Микросервисы",
                    "confidence": 0.85
                }
            }
        }

class TaskMessage(Message):
    """Сообщение о создании задачи"""
    type: Literal[MessageType.TASK] = MessageType.TASK
    metadata: Dict[str, Any] = Field(..., description="Метаданные задачи")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_789",
                "meeting_id": "meet_123",
                "run_id": "run_123",
                "agent_id": "scribe",
                "role": "assistant",
                "type": "task",
                "content": "Создана задача: Настроить CI/CD для микросервисов",
                "created_at": "2024-01-20T10:35:00Z",
                "metadata": {
                    "task_id": "task_123",
                    "priority": "high",
                    "assignee": "devops@company.com",
                    "due_date": "2024-02-01"
                }
            }
        }

class ToolCallMessage(Message):
    """Сообщение о вызове инструмента"""
    type: Literal[MessageType.TOOL_CALL] = MessageType.TOOL_CALL
    metadata: Dict[str, Any] = Field(..., description="Метаданные вызова инструмента")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_012",
                "meeting_id": "meet_123",
                "run_id": "run_123",
                "agent_id": "integrator",
                "role": "tool",
                "type": "tool_call",
                "content": "Создание страницы в Notion с решением",
                "created_at": "2024-01-20T10:40:00Z",
                "metadata": {
                    "tool_id": "notion.decision_log",
                    "status": "started",
                    "args_masked": {"meeting_id": "meet_123"}
                }
            }
        }

class MessageThread(BaseModel):
    """Цепочка связанных сообщений"""
    thread_id: str = Field(..., description="Идентификатор цепочки")
    meeting_id: str = Field(..., description="Идентификатор встречи")
    messages: List[Message] = Field(default_factory=list, description="Сообщения в цепочке")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные цепочки")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "thread_123",
                "meeting_id": "meet_123",
                "messages": [
                    {
                        "id": "msg_123",
                        "meeting_id": "meet_123",
                        "run_id": "run_123",
                        "agent_id": "expert_1",
                        "role": "assistant",
                        "type": "chat",
                        "content": "Предлагаю рассмотреть микросервисы",
                        "created_at": "2024-01-20T10:00:00Z"
                    },
                    {
                        "id": "msg_124",
                        "meeting_id": "meet_123",
                        "run_id": "run_123",
                        "agent_id": "expert_2",
                        "role": "assistant",
                        "type": "chat",
                        "content": "Согласен, но нужно учесть риски",
                        "created_at": "2024-01-20T10:01:00Z",
                        "reply_to": "msg_123"
                    }
                ],
                "metadata": {
                    "topic": "Выбор архитектуры",
                    "status": "active"
                }
            }
        } 