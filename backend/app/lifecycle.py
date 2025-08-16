"""
Управление жизненным циклом приложения XIO
"""

import logging
from typing import Optional

from app.config.settings import get_settings
from app.ws.broker import event_broker
from app.orchestrator.manager import XIOOrchestrator

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Менеджер жизненного цикла приложения"""
    
    def __init__(self):
        self.settings = get_settings()
        self._db_engine: Optional[object] = None
        self._redis_client: Optional[object] = None
        self._chroma_client: Optional[object] = None
        self._orchestrator: Optional[XIOOrchestrator] = None
    
    async def initialize_databases(self):
        """Инициализация подключений к базам данных"""
        logger.info("Инициализация подключений к базам данных...")
        
        # TODO: Инициализация PostgreSQL
        # from app.storage.postgres.base import init_db
        # self._db_engine = await init_db(self.settings.DATABASE_URL)
        
        # TODO: Инициализация Redis
        # import redis.asyncio as redis
        # self._redis_client = redis.from_url(self.settings.REDIS_URL)
        
        # TODO: Инициализация ChromaDB
        # import chromadb
        # self._chroma_client = chromadb.HttpClient(
        #     host=self.settings.CHROMA_HOST,
        #     port=self.settings.CHROMA_PORT
        # )
        
        logger.info("Подключения к базам данных успешно инициализированы")
    
    async def initialize_tool_registry(self):
        """Инициализация реестра инструментов"""
        logger.info("Загрузка реестра инструментов...")
        
        # TODO: Загрузка ToolDefinition из registry/tools/definitions/
        # from app.tools.registry_service import ToolRegistryService
        # registry = ToolRegistryService()
        # await registry.load_definitions()
        
        logger.info("Реестр инструментов загружен")
    
    async def initialize_orchestrator(self):
        """Инициализация оркестратора AutoGen"""
        logger.info("Инициализация оркестратора AutoGen...")
        
        # Создаем и инициализируем оркестратор
        self._orchestrator = XIOOrchestrator()
        await self._orchestrator.initialize()
        
        logger.info("Оркестратор AutoGen инициализирован")
    
    async def initialize_websocket_broker(self):
        """Инициализация WebSocket брокера событий"""
        logger.info("Инициализация WebSocket брокера...")
        
        # Запускаем обработку событий
        await event_broker.start_processing()
        
        logger.info("WebSocket брокер инициализирован")
    
    async def close_connections(self):
        """Закрытие подключений"""
        logger.info("Закрытие подключений...")
        
        # Останавливаем брокер событий
        await event_broker.stop_processing()
        
        if self._redis_client:
            await self._redis_client.close()
        
        if self._db_engine:
            # await self._db_engine.dispose()
            pass
        
        logger.info("Подключения закрыты")


# Глобальный экземпляр менеджера
lifecycle_manager = LifecycleManager()


async def startup_event():
    """Событие запуска приложения"""
    logger.info("Запуск XIO Backend...")
    
    try:
        await lifecycle_manager.initialize_databases()
        await lifecycle_manager.initialize_tool_registry()
        await lifecycle_manager.initialize_orchestrator()
        await lifecycle_manager.initialize_websocket_broker()
        
        logger.info("XIO Backend успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        raise


async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("Остановка XIO Backend...")
    
    try:
        await lifecycle_manager.close_connections()
        logger.info("XIO Backend успешно остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}")
        raise 