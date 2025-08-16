"""
Настройки приложения XIO
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "XIO"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # База данных
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/xio",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # ChromaDB
    CHROMA_HOST: str = Field(default="localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8001, env="CHROMA_PORT")
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        env="CELERY_RESULT_BACKEND"
    )
    
    # AutoGen/LLM настройки
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    DEFAULT_MODEL: str = Field(default="gpt-4", env="DEFAULT_MODEL")
    MAX_TOKENS: int = Field(default=4000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    
    # Notion интеграция
    NOTION_API_KEY: Optional[str] = Field(default=None, env="NOTION_API_KEY")
    NOTION_DATABASE_ID: Optional[str] = Field(default=None, env="NOTION_DATABASE_ID")
    
    # Slack интеграция
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    
    # Telegram интеграция
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    
    # Безопасность
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Лимиты
    MAX_CONCURRENT_RUNS: int = Field(default=10, env="MAX_CONCURRENT_RUNS")
    RUN_TIMEOUT_MINUTES: int = Field(default=60, env="RUN_TIMEOUT_MINUTES")
    MAX_MESSAGE_SIZE: int = Field(default=10000, env="MAX_MESSAGE_SIZE")
    
    # Мониторинг
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(
        default=None,
        env="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    
    # Docker sandbox настройки
    DOCKER_HOST: str = Field(default="unix:///var/run/docker.sock", env="DOCKER_HOST")
    SANDBOX_CPU_LIMIT: str = Field(default="0.5", env="SANDBOX_CPU_LIMIT")
    SANDBOX_MEMORY_LIMIT: str = Field(default="512m", env="SANDBOX_MEMORY_LIMIT")
    SANDBOX_TIMEOUT: int = Field(default=30, env="SANDBOX_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (кешированные)"""
    return Settings() 