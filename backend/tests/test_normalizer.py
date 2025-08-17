"""
Тесты для нормализатора задач
"""

import pytest
from datetime import datetime, timedelta
from app.services.normalizer import ActionItemNormalizer
from app.models import TaskPriority, ValidatedDecisionLog, Alternative

@pytest.fixture
def normalizer():
    return ActionItemNormalizer()

@pytest.fixture
def sample_decision():
    return ValidatedDecisionLog(
        meeting_id="test_meeting",
        title="Выбор архитектуры",
        alternatives=[
            Alternative(option="Вариант 1", pros=["Быстро"], cons=["Дорого"]),
            Alternative(option="Вариант 2", pros=["Дешево"], cons=["Медленно"])
        ],
        rationale="Тестовое обоснование",
        decision="Выбран вариант 1"
    )

def test_extract_basic_task(normalizer):
    text = "Необходимо создать базу данных для проекта."
    candidates = normalizer.extract_candidates(text)
    
    assert len(candidates) == 1
    assert candidates[0].text == "создать базу данных для проекта"
    assert candidates[0].confidence >= 0.5

def test_extract_multiple_tasks(normalizer):
    text = """
    Необходимо настроить CI/CD.
    Задача: обновить документацию.
    Требуется провести нагрузочное тестирование.
    """
    candidates = normalizer.extract_candidates(text)
    
    assert len(candidates) == 3
    tasks = [c.text for c in candidates]
    assert "настроить CI/CD" in tasks
    assert "обновить документацию" in tasks
    assert "провести нагрузочное тестирование" in tasks

def test_priority_detection(normalizer):
    texts = {
        "Критично важно обновить SSL сертификаты!": TaskPriority.CRITICAL,
        "Желательно добавить логирование": TaskPriority.MEDIUM,
        "При возможности улучшить UI": TaskPriority.LOW
    }
    
    for text, expected in texts.items():
        candidates = normalizer.extract_candidates(text)
        assert len(candidates) > 0
        assert candidates[0].metadata["priority"] == expected

def test_deadline_extraction(normalizer):
    now = datetime.now()
    
    texts = {
        "До конца дня настроить мониторинг": now.replace(hour=23, minute=59, second=59).date(),
        "В течение 2 недель разработать API": (now + timedelta(weeks=2)).date(),
        "Необходимо в течение 5 дней исправить баги": (now + timedelta(days=5)).date()
    }
    
    for text, expected_date in texts.items():
        candidates = normalizer.extract_candidates(text)
        assert len(candidates) > 0
        extracted_date = candidates[0].metadata["due_date"]
        assert extracted_date is not None
        assert extracted_date.date() == expected_date

def test_confidence_calculation(normalizer):
    texts = {
        # Высокая уверенность
        "TODO: Создать базу данных PostgreSQL до конца недели": 0.8,
        # Средняя уверенность
        "Можно улучшить производительность": 0.5,
        # Низкая уверенность (короткий текст)
        "Проверить код": 0.4
    }
    
    for text, min_confidence in texts.items():
        candidates = normalizer.extract_candidates(text)
        assert len(candidates) > 0
        assert candidates[0].confidence >= min_confidence

def test_normalize_candidates(normalizer, sample_decision):
    text = """
    Критично важно настроить мониторинг до конца недели.
    Необходимо обновить документацию в течение 3 дней.
    """
    
    candidates = normalizer.extract_candidates(text)
    tasks = normalizer.normalize_candidates(candidates, "test_meeting", sample_decision)
    
    assert len(tasks) > 0
    for task in tasks:
        assert task.meeting_id == "test_meeting"
        assert task.title.endswith(".")
        assert "Контекст решения: " in task.description
        assert task.status == "not_started"
        assert "from_decision" in task.tags

def test_title_normalization(normalizer):
    candidates = normalizer.extract_candidates("необходимо   обновить  систему  ")
    tasks = normalizer.normalize_candidates(candidates, "test_meeting")
    
    assert len(tasks) == 1
    assert tasks[0].title == "Обновить систему."

def test_description_generation(normalizer):
    text = "Критично важно настроить мониторинг до конца недели"
    candidates = normalizer.extract_candidates(text)
    tasks = normalizer.normalize_candidates(candidates, "test_meeting")
    
    assert len(tasks) == 1
    description = tasks[0].description
    
    assert "Контекст:" in description
    assert "Метаданные:" in description
    assert "Приоритет:" in description
    assert "Срок:" in description 