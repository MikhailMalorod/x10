from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ImpactLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"

class Alternative(BaseModel):
    """Вариант решения с pros/cons анализом"""
    option: str = Field(..., description="Вариант решения")
    pros: Optional[List[str]] = Field(default_factory=list, description="Преимущества")
    cons: Optional[List[str]] = Field(default_factory=list, description="Недостатки")

class Risk(BaseModel):
    """Описание риска с оценкой impact/probability"""
    risk: str = Field(..., description="Описание риска")
    impact: ImpactLevel = Field(..., description="Уровень воздействия")
    probability: ImpactLevel = Field(..., description="Вероятность")
    mitigation: Optional[str] = Field(None, description="Меры по снижению риска")

class DecisionLog(BaseModel):
    """Журнал принятого решения"""
    meeting_id: str = Field(..., description="Идентификатор встречи")
    title: str = Field(..., description="Заголовок решения")
    alternatives: List[Alternative] = Field(..., min_items=2, description="Рассмотренные альтернативы")
    rationale: str = Field(..., description="Обоснование принятого решения")
    decision: str = Field(..., description="Финальное принятое решение")
    risks: Optional[List[Risk]] = Field(default_factory=list, description="Выявленные риски")
    participants: Optional[List[str]] = Field(default_factory=list, description="Участники принятия решения")
    date: datetime = Field(default_factory=datetime.now, description="Дата и время принятия решения")

    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": "meet_123",
                "title": "Выбор архитектуры микросервисов",
                "alternatives": [
                    {
                        "option": "Монолитная архитектура",
                        "pros": ["Простота разработки", "Легкость деплоя"],
                        "cons": ["Сложность масштабирования", "Высокая связность"]
                    },
                    {
                        "option": "Микросервисы",
                        "pros": ["Независимое масштабирование", "Изоляция компонентов"],
                        "cons": ["Сложность управления", "Накладные расходы на коммуникацию"]
                    }
                ],
                "rationale": "Микросервисы обеспечивают лучшую масштабируемость и изоляцию",
                "decision": "Использовать микросервисную архитектуру",
                "risks": [
                    {
                        "risk": "Сложность отладки распределенных проблем",
                        "impact": "high",
                        "probability": "medium",
                        "mitigation": "Внедрить распределенную трассировку"
                    }
                ],
                "participants": ["Архитектор", "Tech Lead", "DevOps"],
                "date": "2024-01-20T10:00:00Z"
            }
        }

class ActionItem(BaseModel):
    """Задача, созданная на основе решения"""
    meeting_id: str = Field(..., description="Идентификатор встречи")
    title: str = Field(..., description="Название задачи")
    description: str = Field(..., description="Подробное описание задачи")
    assignee: str = Field(..., description="Ответственный за выполнение")
    due_date: Optional[datetime] = Field(None, description="Срок выполнения")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Приоритет задачи")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="Статус задачи")
    tags: Optional[List[str]] = Field(default_factory=list, description="Теги для категоризации")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="Зависимости от других задач")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Оценка времени выполнения в часах")
    acceptance_criteria: Optional[List[str]] = Field(default_factory=list, description="Критерии приемки")

    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": "meet_123",
                "title": "Внедрить распределенную трассировку",
                "description": "Настроить OpenTelemetry для всех микросервисов",
                "assignee": "devops@company.com",
                "due_date": "2024-02-01T00:00:00Z",
                "priority": "high",
                "status": "not_started",
                "tags": ["infrastructure", "observability"],
                "dependencies": ["setup_monitoring"],
                "estimated_hours": 16,
                "acceptance_criteria": [
                    "Трассировка работает между всеми сервисами",
                    "Latency метрики доступны в Grafana",
                    "Алерты настроены"
                ]
            }
        }

class NotionResponse(BaseModel):
    """Ответ от Notion API при создании страницы/задачи"""
    page_id: str = Field(..., description="ID созданной страницы/задачи в Notion")
    url: str = Field(..., description="URL страницы/задачи в Notion")
    status: str = Field(..., description="Статус операции", pattern="^(created|updated)$") 