"""
Валидаторы для моделей XIO
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator, model_validator
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

    @model_validator(mode='after')
    def validate_decision_in_alternatives(self) -> 'ValidatedDecisionLog':
        """Проверяет, что принятое решение соответствует одной из альтернатив"""
        decision = self.decision
        alternatives = self.alternatives
        
        if not decision or not alternatives:
            return self
        
        # Более мягкая проверка - ищем частичное совпадение
        decision_lower = decision.lower()
        has_match = any(
            alt.option.lower() in decision_lower or decision_lower in alt.option.lower()
            for alt in alternatives
        )
        
        if not has_match:
            raise ValueError("Принятое решение должно соответствовать одной из альтернатив")
        
        return self

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

    @model_validator(mode='after')
    def validate_priority_and_criteria(self) -> 'ValidatedActionItem':
        """Проверяет, что для high/critical задач указаны критерии приемки"""
        priority = self.priority
        criteria = self.acceptance_criteria
        
        if priority in ["high", "critical"] and not criteria:
            # Автоматически добавляем базовые критерии для high приоритета
            self.acceptance_criteria = [
                "Задача выполнена в соответствии с требованиями",
                "Результат протестирован и работает корректно",
                "Документация обновлена"
            ]
        
        return self

class DecisionActionLink(BaseModel):
    """Модель для связи между решением и задачами"""
    decision_log: ValidatedDecisionLog
    action_items: List[ValidatedActionItem] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_meeting_id_consistency(self) -> 'DecisionActionLink':
        """Проверяет, что все задачи относятся к тому же meeting_id, что и решение"""
        decision = self.decision_log
        actions = self.action_items
        
        if not decision or not actions:
            return self
        
        for action in actions:
            if action.meeting_id != decision.meeting_id:
                raise ValueError(f"Action item {action.title} имеет неверный meeting_id")
        
        return self

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