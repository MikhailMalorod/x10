"""
Meetings API endpoints для XIO
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import logging

from app.ws.broker import connection_manager, event_broker
from app.orchestrator.manager import XIOOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Глобальный экземпляр оркестратора (в продакшн должен быть через DI)
orchestrator = XIOOrchestrator()


@router.post("/meetings", status_code=status.HTTP_201_CREATED)
async def create_meeting(meeting_data: Dict[str, Any]) -> Dict[str, Any]:
    """Создать новую встречу"""
    # TODO: Валидация через Pydantic модели
    # TODO: Создание Meeting в БД
    
    meeting_id = "meeting_123"  # Заглушка
    
    logger.info(f"Создана встреча {meeting_id}")
    
    return {
        "id": meeting_id,
        "status": "created",
        "team_id": meeting_data.get("team_id"),
        "topic": meeting_data.get("topic"),
        "agenda": meeting_data.get("agenda")
    }


@router.post("/meetings/{meeting_id}/start", status_code=status.HTTP_200_OK)
async def start_meeting(meeting_id: str, start_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Запустить встречу (создать run)"""
    try:
        if start_data is None:
            start_data = {}
            
        topic = start_data.get("topic", "Обсуждение архитектуры")
        agenda = start_data.get("agenda")
        
        # Запускаем оркестратор
        run_id = await orchestrator.start_run(meeting_id, topic, agenda)
        
        # Отправляем событие о запуске
        await event_broker.emit_event({
            "type": "run_status",
            "meeting_id": meeting_id,
            "run_id": run_id,
            "status": "started"
        })
        
        logger.info(f"Запущена встреча {meeting_id}, run {run_id}")
        
        return {
            "run_id": run_id,
            "meeting_id": meeting_id,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Ошибка запуска встречи {meeting_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.websocket("/meetings/{meeting_id}/stream")
async def meeting_stream(websocket: WebSocket, meeting_id: str):
    """WebSocket стрим событий встречи"""
    try:
        # Подключаем к брокеру
        await connection_manager.connect(websocket, meeting_id)
        
        logger.info(f"WebSocket подключение для встречи {meeting_id}")
        
        # Основной цикл - слушаем сообщения от клиента
        while True:
            try:
                # Получаем сообщения от клиента (для heartbeat, команд и т.д.)
                data = await websocket.receive_text()
                
                # Можем обрабатывать команды от клиента
                if data == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": "now"})
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket ошибка для встречи {meeting_id}: {e}")
    finally:
        await connection_manager.disconnect(websocket)
        logger.info(f"WebSocket отключение для встречи {meeting_id}")


@router.post("/meetings/{meeting_id}/control", status_code=status.HTTP_200_OK)
async def control_meeting(meeting_id: str, control_data: Dict[str, Any]) -> Dict[str, Any]:
    """Управление ходом встречи"""
    action = control_data.get("action")
    
    if action not in ["pause", "resume", "stop", "handoff", "request_alt", "request_risk"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неизвестное действие: {action}"
        )
    
    try:
        # Выполняем действие через оркестратор
        result = False
        
        if action == "pause":
            result = await orchestrator.pause_run()
        elif action == "resume":
            result = await orchestrator.resume_run()
        elif action == "stop":
            result = await orchestrator.stop_run()
        elif action == "request_alt":
            result = await orchestrator.request_alternatives()
        elif action == "request_risk":
            result = await orchestrator.request_risk_assessment()
        
        if result:
            # Отправляем событие об изменении статуса
            await event_broker.emit_event({
                "type": "run_status",
                "meeting_id": meeting_id,
                "run_id": orchestrator._current_run_id,
                "status": action,
                "action": action
            })
        
        logger.info(f"Действие {action} для встречи {meeting_id}: {'успешно' if result else 'неудачно'}")
        
        return {
            "meeting_id": meeting_id,
            "action": action,
            "status": "executed" if result else "failed"
        }
        
    except Exception as e:
        logger.error(f"Ошибка выполнения действия {action} для встречи {meeting_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
async def get_meeting(meeting_id: str) -> Dict[str, Any]:
    """Получить информацию о встрече"""
    # TODO: Получение из БД
    
    # Получаем статус оркестратора
    orchestrator_status = orchestrator.get_status()
    
    # Получаем информацию о WebSocket подключениях
    room_info = connection_manager.get_room_info(meeting_id)
    
    return {
        "id": meeting_id,
        "status": "active" if orchestrator_status["is_running"] else "idle",
        "team_id": "team_123",
        "topic": "Обсуждение архитектуры",
        "created_at": "2024-01-01T00:00:00Z",
        "orchestrator_status": orchestrator_status,
        "websocket_info": room_info
    }


@router.get("/meetings/{meeting_id}/status", status_code=status.HTTP_200_OK)
async def get_meeting_status(meeting_id: str) -> Dict[str, Any]:
    """Получить статус встречи и оркестратора"""
    orchestrator_status = orchestrator.get_status()
    room_info = connection_manager.get_room_info(meeting_id)
    
    return {
        "meeting_id": meeting_id,
        "orchestrator": orchestrator_status,
        "websocket": room_info,
        "timestamp": "now"
    } 