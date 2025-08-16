# XIO: Консилиум экспертов на AutoGen v0.4

XIO — мультиагентная система для управляемых консилиумов экспертов, автоматизирующая поток: подготовка → обсуждение → фиксация решений → задачи → фоллоу‑ап.

## Архитектурные принципы

- **Agent-First**: В центре архитектуры — агенты с четко определенными ролями
- **Service-Oriented & Stateless**: Микросервисная архитектура без состояния
- **Tool-Centric & Secure**: Безопасное исполнение инструментов в песочнице

## Ключевые возможности MVP

- 🤖 **Ролевые агенты**: Модератор, Эксперты, Хронист, Интегратор
- 📋 **Автоматизация решений**: От обсуждения к Notion-задачам
- 🔄 **Политики качества**: Минимум альтернатив, обоснование, оценка рисков
- 📊 **Панель модератора**: Управление ходом встречи в реальном времени
- 🔗 **Интеграции**: Notion, Slack, Telegram из коробки

## Быстрый старт

### Требования

- Python 3.11+
- Docker и Docker Compose
- Node.js 18+ (для UI)

### Запуск локально

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd x10
```

2. **Настройте окружение**
```bash
cp config/env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запустите инфраструктуру**
```bash
cd deploy/compose
docker-compose up -d postgres redis chroma
```

4. **Установите зависимости и запустите backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Проверьте работу**
```bash
curl http://localhost:8000/api/v1/health
```

## Структура проекта

```
x10/
├── DOCS/                    # Документация
│   ├── PLAN.md             # План реализации
│   ├── XIO_Architecture_Document.md
│   └── XIO_Project_Structure_Agreed.md
├── backend/                 # Backend на FastAPI
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── orchestrator/   # AutoGen оркестрация
│   │   ├── agents/         # Ролевые агенты
│   │   ├── tools/          # Система инструментов
│   │   └── integrations/   # Внешние интеграции
│   └── requirements.txt
├── ui/                     # Frontend на React + TypeScript
├── registry/               # Реестр команд и инструментов
├── deploy/                 # Docker и K8s манифесты
└── config/                 # Конфигурационные файлы
```

## API Documentation

После запуска backend доступна интерактивная документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные endpoints

- `POST /api/v1/meetings` - Создать встречу
- `POST /api/v1/meetings/{id}/start` - Запустить консилиум
- `WS /api/v1/meetings/{id}/stream` - WebSocket стрим событий
- `GET /api/v1/meetings/{id}/participants` - Участники встречи
- `GET /api/v1/meetings/{id}/artifacts` - Артефакты (решения, задачи)

## Мониторинг

- Health check: `GET /api/v1/health`
- Readiness: `GET /api/v1/ready`
- Метрики: `GET /api/v1/metrics`

## Разработка

### Первый день (MVP)

Согласно плану реализации в [DOCS/PLAN.md](DOCS/PLAN.md), MVP должен быть готов за 3-5 дней.

**День 1**: Оркестрация и роли
- [x] Базовая структура проекта
- [x] FastAPI с заглушками endpoints
- [ ] Интеграция AutoGen v0.4
- [ ] Базовые роли агентов
- [ ] WebSocket брокер

### Тестирование

```bash
cd backend
pytest tests/
```

### Линтинг

```bash
black app/
isort app/
mypy app/
```

## Интеграции

### Notion
Настройте переменные окружения:
```bash
NOTION_API_KEY=your-api-key
NOTION_DATABASE_ID=your-database-id
```

### Slack
```bash
SLACK_BOT_TOKEN=your-bot-token
SLACK_WEBHOOK_URL=your-webhook-url
```

### OpenAI
```bash
OPENAI_API_KEY=your-api-key
```

## Метрики успеха MVP

- ✅ Запуск базового консилиума
- ⏳ ≥70% встреч завершаются decision log + задачами
- ⏳ Время до решения ≤15 минут
- ⏳ WebSocket latency < 250ms

## Лицензия

[MIT License](LICENSE)

## Вклад в проект

См. [CONTRIBUTING.md](CONTRIBUTING.md) для инструкций по участию в разработке.

## Поддержка

- GitHub Issues для багов и фич
- Документация в папке `DOCS/`
- План разработки в `DOCS/PLAN.md` 