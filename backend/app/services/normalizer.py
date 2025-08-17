"""
Нормализатор для извлечения задач из протокола консилиума
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.models import (
    ValidatedActionItem,
    ValidatedDecisionLog,
    DecisionActionLink,
    TaskPriority,
    TaskStatus
)

class ActionItemCandidate(BaseModel):
    """Кандидат в задачи, извлеченный из текста"""
    text: str
    context: str
    confidence: float
    metadata: Dict[str, Any]

class ActionItemNormalizer:
    """Извлекает и нормализует задачи из протокола консилиума"""

    # Паттерны для извлечения задач
    TASK_PATTERNS = [
        r"(?:необходимо|нужно|требуется|следует)\s+([^\.]+)",
        r"задача[:]\s*([^\.]+)",
        r"(?:создать|разработать|внедрить|настроить|исследовать)\s+([^\.]+)",
        r"(?:TODO|FIXME|XXX)[:]\s*([^\.]+)"
    ]

    # Паттерны для извлечения сроков
    DEADLINE_PATTERNS = {
        r"до конца (дня|недели|месяца|года)": {
            "день": lambda: datetime.now().replace(hour=23, minute=59, second=59),
            "неделя": lambda: datetime.now() + timedelta(days=7),
            "месяц": lambda: datetime.now() + timedelta(days=30),
            "год": lambda: datetime.now().replace(month=12, day=31)
        },
        r"в течение (\d+)\s*(дней|недель|месяцев)": {
            "дней": lambda x: datetime.now() + timedelta(days=int(x)),
            "недель": lambda x: datetime.now() + timedelta(weeks=int(x)),
            "месяцев": lambda x: datetime.now() + timedelta(days=int(x)*30)
        }
    }

    # Ключевые слова для определения приоритета
    PRIORITY_KEYWORDS = {
        TaskPriority.CRITICAL: ["критично", "срочно", "немедленно", "блокер"],
        TaskPriority.HIGH: ["важно", "приоритетно", "необходимо"],
        TaskPriority.MEDIUM: ["желательно", "хорошо бы", "можно"],
        TaskPriority.LOW: ["опционально", "при возможности", "не срочно"]
    }

    def __init__(self):
        self.task_patterns = [re.compile(p, re.IGNORECASE) for p in self.TASK_PATTERNS]
        self.deadline_patterns = {re.compile(k, re.IGNORECASE): v 
                                for k, v in self.DEADLINE_PATTERNS.items()}

    def extract_candidates(self, text: str) -> List[ActionItemCandidate]:
        """Извлекает кандидатов в задачи из текста"""
        candidates = []
        
        # Разбиваем текст на предложения (упрощенно)
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Проверяем каждый паттерн
            for pattern in self.task_patterns:
                match = pattern.search(sentence)
                if match:
                    task_text = match.group(1).strip()
                    
                    # Определяем приоритет
                    priority = self._detect_priority(sentence)
                    
                    # Ищем срок
                    due_date = self._extract_deadline(sentence)
                    
                    # Создаем кандидата
                    candidate = ActionItemCandidate(
                        text=task_text,
                        context=sentence,
                        confidence=self._calculate_confidence(task_text, sentence),
                        metadata={
                            "priority": priority,
                            "due_date": due_date,
                            "extracted_from": "text_pattern"
                        }
                    )
                    candidates.append(candidate)
        
        return candidates

    def _detect_priority(self, text: str) -> TaskPriority:
        """Определяет приоритет задачи по ключевым словам"""
        text = text.lower()
        
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return priority
        
        return TaskPriority.MEDIUM

    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """Извлекает срок выполнения из текста"""
        for pattern, handlers in self.deadline_patterns.items():
            match = pattern.search(text)
            if match:
                groups = match.groups()
                if len(groups) == 1:  # "до конца недели"
                    unit = groups[0].lower()
                    return handlers[unit]()
                elif len(groups) == 2:  # "в течение 2 недель"
                    number, unit = groups
                    unit = unit.lower()
                    return handlers[unit](number)
        return None

    def _calculate_confidence(self, task_text: str, context: str) -> float:
        """Вычисляет уверенность в том, что найдена настоящая задача"""
        confidence = 0.5  # Базовая уверенность
        
        # Длина текста задачи
        if len(task_text) > 10:
            confidence += 0.1
        if len(task_text) > 30:
            confidence += 0.1
            
        # Глагол действия в начале
        if re.match(r"^(создать|разработать|внедрить|настроить|исследовать)", task_text.lower()):
            confidence += 0.2
            
        # Четкие маркеры задач
        if "TODO:" in context or "задача:" in context.lower():
            confidence += 0.2
            
        # Наличие сроков
        if any(pattern.search(context) for pattern in self.deadline_patterns.keys()):
            confidence += 0.1
            
        # Наличие приоритетов
        if any(keyword in context.lower() for keywords in self.PRIORITY_KEYWORDS.values() 
               for keyword in keywords):
            confidence += 0.1
            
        return min(1.0, confidence)

    def normalize_candidates(self, 
                           candidates: List[ActionItemCandidate], 
                           meeting_id: str,
                           decision: Optional[ValidatedDecisionLog] = None) -> List[ValidatedActionItem]:
        """Преобразует кандидатов в валидированные задачи"""
        tasks = []
        
        for candidate in candidates:
            if candidate.confidence < 0.6:  # Пропускаем неуверенные кандидаты
                continue
                
            # Создаем базовую задачу
            task = ValidatedActionItem(
                meeting_id=meeting_id,
                title=self._normalize_title(candidate.text),
                description=self._generate_description(candidate),
                assignee="team@company.com",  # Заглушка, нужна интеграция с сервисом пользователей
                due_date=candidate.metadata.get("due_date"),
                priority=candidate.metadata.get("priority", TaskPriority.MEDIUM),
                status=TaskStatus.NOT_STARTED
            )
            
            # Если есть решение, добавляем контекст
            if decision:
                task.tags = ["from_decision"]
                task.description += f"\n\nКонтекст решения: {decision.title}"
            
            tasks.append(task)
        
        return tasks

    def _normalize_title(self, text: str) -> str:
        """Нормализует заголовок задачи"""
        # Убираем лишние пробелы
        text = " ".join(text.split())
        
        # Первая буква заглавная
        text = text[0].upper() + text[1:]
        
        # Добавляем точку в конце если нет
        if not text.endswith((".", "!", "?")):
            text += "."
            
        return text

    def _generate_description(self, candidate: ActionItemCandidate) -> str:
        """Генерирует описание задачи"""
        description = [
            candidate.text,
            "",
            "Контекст:",
            candidate.context,
            "",
            "Метаданные:",
            f"- Приоритет: {candidate.metadata.get('priority', 'не указан')}",
        ]
        
        if candidate.metadata.get("due_date"):
            description.append(
                f"- Срок: {candidate.metadata['due_date'].strftime('%Y-%m-%d %H:%M')}"
            )
            
        return "\n".join(description) 