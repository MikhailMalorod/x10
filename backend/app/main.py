"""
Главная точка входа для XIO Backend
Консилиум экспертов на базе AutoGen v0.4
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import get_settings
from app.lifecycle import startup_event, shutdown_event
from app.api.v1 import meetings, teams, tools, messages, participants, artifacts, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


def create_app() -> FastAPI:
    """Создание FastAPI приложения с настройкой middleware и маршрутов"""
    settings = get_settings()
    
    app = FastAPI(
        title="XIO: Консилиум экспертов",
        description="Мультиагентная система для управляемых консилиумов экспертов на AutoGen v0.4",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API routes
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(meetings.router, prefix="/api/v1", tags=["meetings"])
    app.include_router(teams.router, prefix="/api/v1", tags=["teams"])
    app.include_router(tools.router, prefix="/api/v1", tags=["tools"])
    app.include_router(messages.router, prefix="/api/v1", tags=["messages"])
    app.include_router(participants.router, prefix="/api/v1", tags=["participants"])
    app.include_router(artifacts.router, prefix="/api/v1", tags=["artifacts"])
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 