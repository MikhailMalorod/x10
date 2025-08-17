"""
Валидаторы для моделей XIO
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator, root_validator
from .artifacts import DecisionLog, ActionItem, Alternative, Risk

class ValidatedDecisionLog(DecisionLog):
    """Расширенная модель DecisionLog с дополнительной валидацией"""

    @validator("alternatives")
    def validate_alternatives_count(cls, v: List[Alternative]) -> List[Alternative]:
        """Проверяет, что есть как минимум 2 альтернативы с разными вариантами"""
        if len(v) < 2:
            raise ValueError("Необходимо как минимум 2 альтернативы")
        
        options = [alt.option for alt in v]
        if len(options) != len(set(options)):
            raise ValueError("Альтернативы должны быть уникальными")
        
        return v

    @validator("risks")
    def validate_risks(cls, v: Optional[List[Risk]]) -> Optional[List[Risk]]:
        """Проверяет, что для high impact рисков указана митигация"""
        if not v:
            return v
        
        for risk in v:
            if risk.impact == "high" and not risk.mitigation:
                raise ValueError(f"Для риска '{risk.risk}' с high impact необходимо указать меры по снижению")
        
        return v

    @root_validator
    def validate_decision_in_alternatives(cls, values: dict) -> dict:
        """Проверяет, что принятое решение соответствует одной из альтернатив"""
        decision = values.get("decision")
        alternatives = values.get("alternatives", [])
        
        if not decision or not alternatives:
            return values
        
        if not any(decision.lower() in alt.option.lower() for alt in alternatives):
            raise ValueError("Принятое решение должно соответствовать одной из альтернатив")
        
        return values

class ValidatedActionItem(ActionItem):
    """Расширенная модель ActionItem с дополнительной валидацией"""

    @validator("due_date")
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Проверяет, что срок выполнения в будущем"""
        if v and v < datetime.now():
            raise ValueError("Срок выполнения должен быть в будущем")
        return v

    @validator("estimated_hours")
    def validate_estimated_hours(cls, v: Optional[float]) -> Optional[float]:
        """Проверяет оценку времени"""
        if v is not None:
            if v <= 0:
                raise ValueError("Оценка времени должна быть положительной")
            if v > 160:  # ~месяц работы
                raise ValueError("Оценка времени не может превышать 160 часов")
        return v

    @validator("acceptance_criteria")
    def validate_acceptance_criteria(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Проверяет критерии приемки"""
        if not v:
            return v
        
        # Убираем дубликаты и пустые строки
        v = list(filter(None, set(v)))
        
        # Проверяем минимальную длину каждого критерия
        for criterion in v:
            if len(criterion) < 10:
                raise ValueError(f"Критерий '{criterion}' слишком короткий (минимум 10 символов)")
        
        return v

    @root_validator
    def validate_priority_and_criteria(cls, values: dict) -> dict:
        """Проверяет, что для high/critical задач указаны критерии приемки"""
        priority = values.get("priority")
        criteria = values.get("acceptance_criteria", [])
        
        if priority in ["high", "critical"] and not criteria:
            raise ValueError(f"Для задач с приоритетом {priority} необходимо указать критерии приемки")
        
        return values

class DecisionActionLink(BaseModel):
    """Модель для связи между решением и задачами"""
    decision_log: ValidatedDecisionLog
    action_items: List[ValidatedActionItem] = Field(default_factory=list)

    @root_validator
    def validate_meeting_id_consistency(cls, values: dict) -> dict:
        """Проверяет, что все задачи относятся к тому же meeting_id, что и решение"""
        decision = values.get("decision_log")
        actions = values.get("action_items", [])
        
        if not decision or not actions:
            return values
        
        for action in actions:
            if action.meeting_id != decision.meeting_id:
                raise ValueError(f"Action item {action.title} имеет неверный meeting_id")
        
        return values

    @validator("action_items")
    def validate_action_items_dependencies(cls, v: List[ValidatedActionItem]) -> List[ValidatedActionItem]:
        """Проверяет корректность зависимостей между задачами"""
        if not v:
            return v
        
        # Создаем множество всех ID задач
        task_ids = {task.title for task in v}  # Используем title как ID
        
        # Проверяем, что все зависимости существуют
        for task in v:
            for dep in task.dependencies:
                if dep not in task_ids:
                    raise ValueError(f"Задача {task.title} зависит от несуществующей задачи {dep}")
        
        return v 