# Утвержденная структура проекта XIO (CE/EE) — консилиум экспертов на AutoGen v0.4

Версия: 1.0  
Дата: [Текущая дата]

Документ фиксирует согласованную структуру репозитория XIO и детально описывает назначение директорий и файлов, их взаимодействие и границы CE/EE (Open‑Core). Основано на документах: `XIO_ at_AutoGen v0.4.md`, `XIO_Architecture_Document.md`, `CHAT_dop.md`, `CHAT_UI_dop.md`.

## Принципы

- Agent‑First, Service‑Oriented & Stateless, Tool‑Centric & Secure.
- Чатовый UX: WS‑стрим событий, lazy‑load истории, треды инструментов, артефакты.
- CE/EE разделение: базовая функциональность в CE; расширенные политики, SSO/RBAC, шина и расширенная наблюдаемость — в EE (`/ee`).

## Дерево директорий (высокоуровневое)

```plaintext
x10/
├─ DOCS/
│  ├─ XIO_ at_AutoGen v0.4.md
│  ├─ XIO_Architecture_Document.md
│  ├─ CHAT_dop.md
│  ├─ CHAT_UI_dop.md
│  └─ XIO_Project_Structure_Agreed.md          ← Этот документ
│
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ lifecycle.py
│  │  ├─ config/
│  │  │  ├─ settings.py
│  │  │  └─ __init__.py
│  │  ├─ api/
│  │  │  └─ v1/
│  │  │     ├─ meetings.py
│  │  │     ├─ teams.py
│  │  │     ├─ tools.py
│  │  │     ├─ messages.py
│  │  │     ├─ participants.py
│  │  │     ├─ artifacts.py
│  │  │     ├─ health.py
│  │  │     └─ __init__.py
│  │  ├─ models/
│  │  │  ├─ meetings.py
│  │  │  ├─ teams.py
│  │  │  ├─ tools.py
│  │  │  ├─ artifacts.py
│  │  │  └─ common.py
│  │  ├─ ws/
│  │  │  ├─ broker.py
│  │  │  └─ serializers.py
│  │  ├─ orchestrator/
│  │  │  ├─ manager.py
│  │  │  ├─ speaker_selection/
│  │  │  │  ├─ round_robin.py
│  │  │  │  ├─ auto.py
│  │  │  │  └─ custom_selector.py
│  │  │  ├─ policies/
│  │  │  │  ├─ consensus.py
│  │  │  │  └─ completion_checks.py
│  │  │  └─ state/
│  │  │     ├─ run_state.py
│  │  │     └─ events.py
│  │  ├─ agents/
│  │  │  ├─ moderator.py
│  │  │  ├─ expert.py
│  │  │  ├─ scribe.py
│  │  │  └─ integrator.py
│  │  ├─ tools/
│  │  │  ├─ executor.py
│  │  │  ├─ registry_service.py
│  │  │  ├─ schemas/
│  │  │  │  ├─ notion.decision_log.json
│  │  │  │  └─ notion.task.json
│  │  │  └─ sandbox/
│  │  ├─ services/
│  │  │  ├─ meetings_service.py
│  │  │  ├─ teams_service.py
│  │  │  ├─ tools_service.py
│  │  │  ├─ rag_service.py
│  │  │  └─ integrations_service.py
│  │  ├─ storage/
│  │  │  ├─ postgres/
│  │  │  │  ├─ base.py
│  │  │  │  ├─ models.py
│  │  │  │  └─ repositories/
│  │  │  │     ├─ meetings_repo.py
│  │  │  │     ├─ messages_repo.py
│  │  │  │     ├─ tools_repo.py
│  │  │  │     └─ teams_repo.py
│  │  │  ├─ redis/
│  │  │  └─ chroma/
│  │  ├─ integrations/
│  │  │  ├─ notion/
│  │  │  │  ├─ client.py
│  │  │  │  └─ mappers.py
│  │  │  ├─ slack/
│  │  │  │  └─ client.py
│  │  │  └─ telegram/
│  │  │     └─ client.py
│  │  ├─ observability/
│  │  │  ├─ logging.py
│  │  │  ├─ tracing.py
│  │  │  └─ metrics.py
│  │  ├─ security/
│  │  │  ├─ auth.py
│  │  │  ├─ secrets.py
│  │  │  └─ privacy.py
│  │  └─ ee/
│  │     ├─ rbac/
│  │     ├─ sso/
│  │     ├─ policies/
│  │     └─ grpc/
│  ├─ workers/
│  │  ├─ run_worker.py
│  │  └─ tool_worker.py
│  ├─ migrations/
│  ├─ tests/
│  ├─ requirements.txt
│  └─ pyproject.toml
│
├─ ui/
│  ├─ src/
│  │  ├─ app/
│  │  │  ├─ routes.tsx
│  │  │  └─ AppShell.tsx
│  │  ├─ design-system/
│  │  │  ├─ tokens/{colors.json,typography.json,space.json,motion.json}
│  │  │  ├─ css/{base.css,tokens.css,theme.light.css,theme.dark.css,theme.brand.default.css}
│  │  │  ├─ ThemeProvider.tsx
│  │  │  └─ index.ts
│  │  ├─ components/
│  │  │  ├─ primitives/
│  │  │  ├─ layout/SplitPane.tsx
│  │  │  ├─ chat/{ParticipantsSidebar.tsx,ConversationPane.tsx}
│  │  │  ├─ chat/messages/{AgentMessage.tsx,ToolCallThread.tsx,ArtifactCard.tsx}
│  │  │  ├─ chat/moderator/{ModeratorPanel.tsx,RunControls.tsx}
│  │  │  └─ feedback/{Toasts.tsx,Banners.tsx}
│  │  ├─ pages/Meetings/{ListPage.tsx,DetailPage.tsx}
│  │  ├─ services/{api.ts,ws.ts}
│  │  ├─ store/{meetingStore.ts,uiStore.ts}
│  │  ├─ hooks/{useChatStream.ts,useRunControl.ts}
│  │  ├─ utils/{messageFormat.ts,i18n.ts,featureFlags.ts}
│  │  ├─ index.css
│  │  └─ main.tsx
│  ├─ public/
│  ├─ package.json
│  ├─ tailwind.config.ts
│  ├─ postcss.config.js
│  └─ tsconfig.json
│
├─ registry/
│  ├─ tools/{definitions/*.json,templates/*}
│  └─ teams/samples/*.json
│
├─ deploy/
│  ├─ docker/{Dockerfile.backend,Dockerfile.worker,Dockerfile.ui,Dockerfile.tool_sandbox}
│  ├─ compose/docker-compose.yml
│  ├─ k8s/{backend-deploy.yaml,worker-deploy.yaml,ui-deploy.yaml,redis.yaml,postgres.yaml,chroma.yaml,ingress.yaml,externalsecrets.yaml}
│  └─ helm/
│
├─ config/{.env.example,logging.yaml,ui-brand.config.json}
├─ scripts/{make.ps1,db_migrate.ps1,seed_demo.ps1}
├─ openapi/openapi-v1.json
├─ .github/workflows/ci.yml
├─ LICENSE
├─ README.md
├─ CONTRIBUTING.md
└─ CODE_OF_CONDUCT.md
```

## Расшифровка и назначение компонентов

### DOCS/
- `XIO_ at_AutoGen v0.4.md`: базовая продуктово‑архитектурная спецификация на AutoGen v0.4.
- `XIO_Architecture_Document.md`: детальная архитектура (компоненты, стек, API, модели, диаграммы, WS‑события).
- `CHAT_dop.md`: специфика чатового UX/потоков событий, API дополнения, модель БД для ToolThreads и Participants snapshot.
- `CHAT_UI_dop.md`: UI‑архитектура на shadcn/ui + Radix + Tailwind, токены/темизация, ключевые компоненты.
- `XIO_Project_Structure_Agreed.md`: текущий документ — утвержденная структура.

### backend/app/
- `main.py`: точка входа FastAPI; регистрация REST/WS маршрутов, CORS, middlewares, наблюдаемость.
- `lifecycle.py`: startup/shutdown hooks; подключение БД/кешей/очередей; прогрев реестров инструментов.

#### config/
- `settings.py`: Pydantic Settings (PostgreSQL, Redis, ChromaDB, очереди, OTel, интеграции Notion/Slack и пр.).

#### api/v1/
- `meetings.py`: 
  - POST `/meetings` (создание Meeting), POST `/meetings/{id}/start` (запуск run),
  - WS `/meetings/{id}/stream` (StreamEvent),
  - POST `/meetings/{id}/control` (pause/resume/stop/handoff/request_alt/request_risk).
- `teams.py`: CRUD Team, `/teams/{id}/config`, импорт конфигов из AutoGen Studio.
- `tools.py`: GET `/tools/available` (реестр ToolDefinition), CRUD ToolDefinition/ToolInstance (с RBAC/scopes).
- `messages.py`: GET `/meetings/{id}/messages?page=…` (пагинация истории), POST (опц.) пользовательские сообщения.
- `participants.py`: GET `/meetings/{id}/participants` (состав/статусы/roles/speaking/next/tool badges).
- `artifacts.py`: доступ к артефактам (decision logs, ссылки на Notion/внешние системы).
- `health.py`: `/health`, `/ready`, `/metrics`.

#### models/
- Контракты (Pydantic): `MeetingCreate`, `RunControl`, `StreamEvent` (union типов), `ChatMessage`, схемы `Team/Tools/Artifacts/Common`.

#### ws/
- `broker.py`: маршрутизация событий в комнаты (room = meeting_id), heartbeat/reconnect, backpressure.
- `serializers.py`: приведение внутренних событий оркестратора к унифицированному `StreamEvent` (participant_updated, chat_message, tool_call, artifact, run_status), маскирование аргументов инструментов.

#### orchestrator/
- `manager.py`: обертка над AutoGen GroupChatManager, run‑lifecycle, pause/resume/stop, ручной `handoff`.
- `speaker_selection/`: стратегии выбора спикера: `round_robin`, `auto`, `custom_selector` (CE/EE расширяемо).
- `policies/`: консенсус/качество: минимум альтернатив, rationale_required, risk_cost_required, completion checks.
- `state/`: `run_state.py` (speaking_now/next_speaker/timers), `events.py` (внутренние события для WS сериализаторов).

#### agents/
- Ролевые `AssistantAgent`: `moderator`, `expert`, `scribe`, `integrator` (настройка промптов/моделей/инструментов).

#### tools/
- `executor.py`: исполнение инструментов через UserProxy (Docker‑песочница), лимиты CPU/RAM/NET/timeout, маскирование секретов, логирование, идемпотентность.
- `registry_service.py`: работа с `ToolDefinition/ToolInstance`, JSON Schema‑валидация, scopes (agent/team/global), разрешения (RBAC), rate‑limits.
- `schemas/`: JSON‑описания системных инструментов (подписи для LLM). Примеры: `notion.decision_log.json`, `notion.task.json`.
- `sandbox/`: политики песочницы и сетевые allowlists (egress‑доменов).

#### services/
- Прикладные сервисы (чистая логика, без транспорта/ORM):
  - `meetings_service.py`: создание/запуск, управление run, сбор/агрегация метрик.
  - `teams_service.py`: версионирование Team, дефолты, селектор спикеров по умолчанию.
  - `tools_service.py`: резолв ToolInstance, лимиты/идемпотентность вызовов.
  - `rag_service.py`: извлечение контекста из ChromaDB.
  - `integrations_service.py`: обертки Notion/Slack/Telegram, нормализация payload.

#### storage/
- `postgres/`: SQLAlchemy ORM, модели таблиц: `teams`, `agents`, `tool_definitions`, `tool_instances`, `meetings`, `runs`, `messages`, `tool_call_threads`, `participants_snapshot`, `artifacts`, `audit_logs`. Репозитории для операций.
- `redis/`: живое состояние run (speaking_now/timers/next_speaker), кеши для быстрого доступа.
- `chroma/`: векторный индекс (повестки/фрагменты истории/документы) для RAG.

#### integrations/
- `notion/`: `client.py` (идемпотентное создание decision log/tasks по `meeting_id`), `mappers.py` (преобразование данных).
- `slack/`, `telegram/`: клиенты отправки резюме/фоллоу‑апов.

#### observability/
- `logging.py`, `tracing.py` (OTel, корреляция `run_id/meeting_id/agent_id`), `metrics.py` (Prometheus).

#### security/
- `auth.py`: (CE) базовая auth/JWT; (EE) SSO (OIDC/SAML).
- `secrets.py`: интеграции с Vault/KMS; `secrets_ref` вместо инлайна.
- `privacy.py`: маскирование секретов в логах, политики приватности, уровни доступа.

#### ee/
- Расширения Enterprise: `rbac/` (организационные роли/политики), `sso/`, `policies/` (OPA‑движок для селектора/консенсуса), `grpc/` (внутренняя шина, опционально).

### backend/workers/
- `run_worker.py`: жизненный цикл run (Celery tasks), координация с оркестратором.
- `tool_worker.py`: вынесенное исполнение инструментов (offload) с учетом лимитов/ретраев.

### backend/migrations/
- Alembic‑миграции схемы БД; версионирование и откаты.

### backend/tests/
- `unit/`, `integration/`, `e2e/`: тесты оркестрации, WS‑событий, идемпотентности интеграций.

### ui/
- React + TypeScript + Vite; дизайн‑система (shadcn/ui + Radix + Tailwind), токены/темизация.
- `app/`: маршрутизация и каркас `AppShell` (HeaderBar + SplitPane).
- `design-system/`: токены (`colors/typography/space/motion`), CSS‑переменные, темы (light/dark/brand), `ThemeProvider`.
- `components/`: 
  - `primitives/` — форки shadcn, унифицированные под токены/темы.
  - `layout/SplitPane.tsx` — разделитель левая/правая панели.
  - `chat/ParticipantsSidebar.tsx` — список агентов (роль, speaking/next, tool badges, контекстные действия модератора).
  - `chat/ConversationPane.tsx` — лента сообщений (виртуализация, markdown, mentions).
  - `chat/messages/*` — `AgentMessage`, `ToolCallThread` (стадии/прогресс/логи, masked args), `ArtifactCard` (Decision Log/Task + ссылки).
  - `chat/moderator/*` — `ModeratorPanel`, `RunControls` (pause/resume/stop, handoff, запрос альтернатив/рисков).
  - `feedback/*` — `Toasts`, `Banners` (WS‑reconnect, глобальные статусы).
- `pages/Meetings/*` — список и деталка встречи (подключение WS, lazy‑load истории).
- `services/{api.ts,ws.ts}` — REST/WS клиенты (reconnect/backoff/heartbeat, сериализация/десериализация событий).
- `store/{meetingStore.ts,uiStore.ts}` — Zustand/RTK: participants/messages/toolThreads/artifacts/runState; батч‑обновления.
- `hooks/{useChatStream.ts,useRunControl.ts}` — подписка на WS, обертки POST /control.
- `utils/{messageFormat.ts,i18n.ts,featureFlags.ts}` — markdown/mentions, локализация, флаги.
- `tailwind.config.ts`, `index.css` — интеграция CSS vars, подключение тем.

### registry/
- `tools/definitions/*.json` — подписи `ToolDefinition` (JSON Schema, returns, constraints, network policy) — источник правды для ассистента и валидации.
- `tools/templates/*` — примерные `ToolInstance` без секретов (для быстрого старта).
- `teams/samples/*.json` — образцы конфигураций Team (Moderator/Experts/Scribe/Integrator, политики).

### deploy/
- `docker/*` — Dockerfile для backend/worker/ui и базовый образ песочницы инструментов.
- `compose/docker-compose.yml` — локальная разработка (Postgres/Redis/Chroma/UI/Backend/Workers).
- `k8s/*` — манифесты Kubernetes (CE): Deployment/StatefulSet/Ingress/ExternalSecrets.
- `helm/` — (опц.) Helm‑чарт.

### config/
- `.env.example` — переменные окружения (без секретов);
- `logging.yaml` — конфигурация логирования;
- `ui-brand.config.json` — карта брендов (логотипы, палитры, favicon).

### scripts/
- `make.ps1` — удобные команды для Windows (линт/тест/сборка/миграции/запуск локально).
- `db_migrate.ps1` — обертка миграций Alembic.
- `seed_demo.ps1` — демо‑контент (team, meeting, сообщения, tool threads, артефакты).

### openapi/
- `openapi-v1.json` — экспорт спецификации API для клиентов/интеграций.

### .github/
- `workflows/ci.yml` — линт/тест/сборка образов, security‑проверки, публикация артефактов.

### LICENSE, README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md
- Лицензия, гайд по запуску/вкладыванию, кодекс поведения — стандартные файлы OSS.

## Взаимодействие компонентов (кратко)

- UI ↔ Backend: REST (создание/управление), WS (StreamEvent: `participant_updated | chat_message | tool_call | artifact | run_status`).
- Backend ↔ Оркестратор: запуск run, speaker selection, события в WS, фиксация истории/артефактов.
- Оркестратор ↔ UserProxy: безопасное исполнение инструментов (Docker‑песочница) с JSON Schema‑валидацией, маскированием и идемпотентностью.
- Backend ↔ Интеграции: Notion/Slack/Telegram (через `integrations_service`), RAG (ChromaDB).

## CE/EE разделение

- CE: базовый Orchestrator (round_robin/auto), Teams/Meetings, Tools (реестр/экземпляры), WS‑стрим и чатовый UX, Redis/PostgreSQL/Chroma, базовые метрики и аудит.
- EE: SSO (OIDC/SAML), расширенный RBAC/org, OPA‑политики селектора/консенсуса, квоты/лимиты на run/инструменты, приватный marketplace инструментов, расширенная наблюдаемость (OTel traces/metrics), внутренняя gRPC‑шина, data residency.

## Глоссарий ключевых сущностей

- Team: состав агентов/политики/дефолты/привязки инструментов; версионируется, фиксируется на run.
- Meeting: инстанс встречи на базе Team (topic/agenda/config_override).
- Run: выполнение GroupChatManager с историей/событиями; управляется control (pause/resume/stop/handoff).
- Agent: ролевой AssistantAgent (moderator/expert/scribe/integrator).
- ToolDefinition: системная сигнатура инструмента (JSON Schema, returns, constraints, network policy).
- ToolInstance: пользовательская конкретизация инструмента (parameters, secrets_ref, scope, permissions, rate limits).
- ToolCallThread: сущность треда вызова инструмента (started/progress/finished/error, masked args, logs, result).
- Artifact: материализация результата (decision log/task) с внешними ссылками (e.g., Notion URL).
- Participant Snapshot: снапшот состава участников/ролей на момент run (auditability).

Документ предназначен для всех участников проекта и должен использоваться как основной ориентир при разработке, ревью PR и планировании задач. 