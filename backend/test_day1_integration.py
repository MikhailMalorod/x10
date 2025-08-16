"""
Интеграционный тест для проверки компонентов XIO MVP Day 1
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты для тестирования
try:
    from app.main import app
    from app.orchestrator.manager import XIOOrchestrator
    from app.ws.broker import connection_manager, event_broker
    from app.config.settings import get_settings
    logger.info("✅ Все модули импортированы успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    raise


class Day1IntegrationTest:
    """Тестирование интеграции всех компонентов Дня 1"""
    
    def __init__(self):
        self.orchestrator = XIOOrchestrator()
        self.test_results = {}
        
    async def test_1_config_loading(self) -> bool:
        """Тест 1: Загрузка конфигурации"""
        logger.info("🧪 Тест 1: Загрузка конфигурации...")
        
        try:
            settings = get_settings()
            required_settings = [
                'APP_NAME', 'DEBUG', 'HOST', 'PORT',
                'DATABASE_URL', 'REDIS_URL', 'OPENAI_API_KEY'
            ]
            
            for setting in required_settings:
                if not hasattr(settings, setting):
                    logger.error(f"❌ Отсутствует настройка: {setting}")
                    return False
            
            logger.info(f"✅ Конфигурация загружена: APP_NAME={settings.APP_NAME}")
            self.test_results['config_loading'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            self.test_results['config_loading'] = False
            return False
    
    async def test_2_orchestrator_initialization(self) -> bool:
        """Тест 2: Инициализация оркестратора"""
        logger.info("🧪 Тест 2: Инициализация оркестратора...")
        
        try:
            await self.orchestrator.initialize()
            
            # Проверяем базовые методы
            status = self.orchestrator.get_status()
            expected_keys = ['is_running', 'current_run_id', 'agents_count', 'has_team']
            
            for key in expected_keys:
                if key not in status:
                    logger.error(f"❌ Отсутствует ключ статуса: {key}")
                    return False
            
            logger.info(f"✅ Оркестратор инициализирован: {status}")
            self.test_results['orchestrator_init'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации оркестратора: {e}")
            self.test_results['orchestrator_init'] = False
            return False
    
    async def test_3_websocket_broker(self) -> bool:
        """Тест 3: WebSocket брокер событий"""
        logger.info("🧪 Тест 3: WebSocket брокер событий...")
        
        try:
            # Запускаем брокер вручную для тестирования
            if not event_broker._is_processing:
                await event_broker.start_processing()
                logger.info("✅ Брокер событий запущен для тестирования")
            
            # Тестируем создание событий
            test_event = {
                "type": "agent_message",
                "meeting_id": "test_meeting_123",
                "agent_id": "test_agent",
                "content": "Тестовое сообщение",
                "timestamp": datetime.now().isoformat()
            }
            
            # Добавляем событие в брокер
            await event_broker.emit_event(test_event)
            
            # Проверяем, что брокер обрабатывает события
            if not event_broker._is_processing:
                logger.error("❌ Брокер событий не запущен")
                return False
            
            logger.info("✅ WebSocket брокер работает корректно")
            self.test_results['websocket_broker'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка WebSocket брокера: {e}")
            self.test_results['websocket_broker'] = False
            return False
    
    async def test_4_orchestrator_lifecycle(self) -> bool:
        """Тест 4: Жизненный цикл оркестратора"""
        logger.info("🧪 Тест 4: Жизненный цикл оркестратора...")
        
        try:
            # Тестируем запуск run
            run_id = await self.orchestrator.start_run(
                meeting_id="test_meeting_456",
                topic="Тестирование жизненного цикла"
            )
            
            if not run_id:
                logger.error("❌ Не удалось создать run_id")
                return False
            
            # Проверяем статус
            status = self.orchestrator.get_status()
            if not status['is_running']:
                logger.error("❌ Run не запущен")
                return False
            
            # Тестируем паузу
            pause_result = await self.orchestrator.pause_run()
            if not pause_result:
                logger.error("❌ Не удалось поставить на паузу")
                return False
            
            # Тестируем возобновление
            resume_result = await self.orchestrator.resume_run()
            if not resume_result:
                logger.error("❌ Не удалось возобновить")
                return False
            
            # Тестируем остановку
            stop_result = await self.orchestrator.stop_run()
            if not stop_result:
                logger.error("❌ Не удалось остановить")
                return False
            
            logger.info(f"✅ Жизненный цикл оркестратора работает: {run_id}")
            self.test_results['orchestrator_lifecycle'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка жизненного цикла оркестратора: {e}")
            self.test_results['orchestrator_lifecycle'] = False
            return False
    
    async def test_5_notion_schemas(self) -> bool:
        """Тест 5: Валидация JSON схем Notion"""
        logger.info("🧪 Тест 5: Валидация JSON схем Notion...")
        
        try:
            # Загружаем схемы
            with open('app/tools/schemas/notion.decision_log.json', 'r', encoding='utf-8') as f:
                decision_log_schema = json.load(f)
            
            with open('app/tools/schemas/notion.task.json', 'r', encoding='utf-8') as f:
                task_schema = json.load(f)
            
            # Проверяем обязательные поля
            required_decision_fields = ['definition_id', 'name', 'description', 'json_schema']
            required_task_fields = ['definition_id', 'name', 'description', 'json_schema']
            
            for field in required_decision_fields:
                if field not in decision_log_schema:
                    logger.error(f"❌ Отсутствует поле в decision_log: {field}")
                    return False
            
            for field in required_task_fields:
                if field not in task_schema:
                    logger.error(f"❌ Отсутствует поле в task: {field}")
                    return False
            
            logger.info("✅ JSON схемы Notion валидны")
            self.test_results['notion_schemas'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации схем Notion: {e}")
            self.test_results['notion_schemas'] = False
            return False
    
    async def test_6_fastapi_app(self) -> bool:
        """Тест 6: FastAPI приложение"""
        logger.info("🧪 Тест 6: FastAPI приложение...")
        
        try:
            # Проверяем, что приложение создано
            if not app:
                logger.error("❌ FastAPI приложение не создано")
                return False
            
            # Проверяем роутеры
            routes = [route.path for route in app.routes if hasattr(route, 'path')]
            expected_routes = [
                '/api/v1/health',
                '/api/v1/meetings',
                '/api/v1/teams',
                '/api/v1/tools/available',  # Правильный путь
                '/api/v1/meetings/{meeting_id}/messages',  # Правильный путь
                '/api/v1/meetings/{meeting_id}/participants',  # Правильный путь
                '/api/v1/meetings/{meeting_id}/artifacts'  # Правильный путь
            ]
            
            for route in expected_routes:
                if route not in routes:
                    logger.error(f"❌ Отсутствует роут: {route}")
                    return False
            
            logger.info(f"✅ FastAPI приложение создано с {len(routes)} роутами")
            self.test_results['fastapi_app'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка FastAPI приложения: {e}")
            self.test_results['fastapi_app'] = False
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        logger.info("🚀 Запуск интеграционных тестов XIO MVP Day 1...")
        
        tests = [
            self.test_1_config_loading,
            self.test_2_orchestrator_initialization,
            self.test_3_websocket_broker,
            self.test_4_orchestrator_lifecycle,
            self.test_5_notion_schemas,
            self.test_6_fastapi_app
        ]
        
        results = {}
        for test in tests:
            try:
                result = await test()
                results[test.__name__] = result
            except Exception as e:
                logger.error(f"❌ Критическая ошибка в тесте {test.__name__}: {e}")
                results[test.__name__] = False
        
        return results
    
    def print_summary(self):
        """Вывод итогового отчета"""
        logger.info("\n" + "="*60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ ПО ТЕСТИРОВАНИЮ ДНЯ 1")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"📈 Всего тестов: {total_tests}")
        logger.info(f"✅ Успешно: {passed_tests}")
        logger.info(f"❌ Провалено: {failed_tests}")
        logger.info(f"📊 Успешность: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n🔍 Детальные результаты:")
        for test_name, result in self.test_results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            logger.info(f"  {test_name}: {status}")
        
        if failed_tests == 0:
            logger.info("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! День 1 полностью готов!")
        else:
            logger.info(f"\n⚠️  Требуется исправление {failed_tests} тестов")
        
        logger.info("="*60)


async def main():
    """Главная функция тестирования"""
    tester = Day1IntegrationTest()
    
    try:
        results = await tester.run_all_tests()
        tester.test_results = results
        tester.print_summary()
        
        # Возвращаем код выхода
        failed_count = sum(1 for result in results.values() if not result)
        exit_code = 0 if failed_count == 0 else 1
        return exit_code
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка тестирования: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 