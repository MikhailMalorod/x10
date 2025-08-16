"""
WebSocket брокер для XIO событий
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSConnectionManager:
    """Менеджер WebSocket подключений для meeting rooms"""
    
    def __init__(self):
        # meeting_id -> set of websockets
        self._rooms: Dict[str, Set[WebSocket]] = {}
        # websocket -> meeting_id mapping для быстрого поиска
        self._connections: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, meeting_id: str):
        """Подключить WebSocket к комнате встречи"""
        await websocket.accept()
        
        if meeting_id not in self._rooms:
            self._rooms[meeting_id] = set()
        
        self._rooms[meeting_id].add(websocket)
        self._connections[websocket] = meeting_id
        
        logger.info(f"WebSocket подключен к meeting {meeting_id}. Всего в комнате: {len(self._rooms[meeting_id])}")
        
        # Отправляем приветственное сообщение
        await self._send_to_websocket(websocket, {
            "type": "connection_established",
            "payload": {
                "meeting_id": meeting_id,
                "connected_at": datetime.now().isoformat(),
                "participants_count": len(self._rooms[meeting_id])
            }
        })
    
    async def disconnect(self, websocket: WebSocket):
        """Отключить WebSocket"""
        meeting_id = self._connections.get(websocket)
        
        if meeting_id and meeting_id in self._rooms:
            self._rooms[meeting_id].discard(websocket)
            
            # Удаляем пустые комнаты
            if not self._rooms[meeting_id]:
                del self._rooms[meeting_id]
            
            logger.info(f"WebSocket отключен от meeting {meeting_id}")
        
        if websocket in self._connections:
            del self._connections[websocket]
    
    async def broadcast_to_meeting(self, meeting_id: str, message: Dict[str, Any]):
        """Отправить сообщение всем подключенным к встрече"""
        if meeting_id not in self._rooms:
            logger.warning(f"Нет активных подключений для meeting {meeting_id}")
            return
        
        # Копируем set чтобы избежать изменения во время итерации
        connections = self._rooms[meeting_id].copy()
        
        failed_connections = []
        for websocket in connections:
            try:
                await self._send_to_websocket(websocket, message)
            except Exception as e:
                logger.error(f"Ошибка отправки в WebSocket: {e}")
                failed_connections.append(websocket)
        
        # Удаляем сломанные подключения
        for websocket in failed_connections:
            await self.disconnect(websocket)
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """Отправить сообщение в конкретный WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение в WebSocket: {e}")
            raise
    
    def get_room_info(self, meeting_id: str) -> Dict[str, Any]:
        """Получить информацию о комнате"""
        return {
            "meeting_id": meeting_id,
            "active_connections": len(self._rooms.get(meeting_id, [])),
            "is_active": meeting_id in self._rooms
        }


class XIOEventBroker:
    """Брокер событий для координации между оркестратором и WebSocket"""
    
    def __init__(self, connection_manager: WSConnectionManager):
        self.connection_manager = connection_manager
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_processing = False
    
    async def start_processing(self):
        """Запустить обработку событий"""
        if self._is_processing:
            return
        
        self._is_processing = True
        asyncio.create_task(self._process_events())
        logger.info("Запущена обработка XIO событий")
    
    async def _process_events(self):
        """Основной цикл обработки событий"""
        while self._is_processing:
            try:
                # Ждем события из очереди
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._handle_event(event)
            except asyncio.TimeoutError:
                # Нормальный timeout для проверки флага
                continue
            except Exception as e:
                logger.error(f"Ошибка обработки события: {e}")
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Обработать событие и отправить в WebSocket"""
        meeting_id = event.get("meeting_id")
        if not meeting_id:
            logger.warning("Событие без meeting_id, пропускаем")
            return
        
        # Преобразуем в формат StreamEvent
        stream_event = self._to_stream_event(event)
        
        # Отправляем в комнату встречи
        await self.connection_manager.broadcast_to_meeting(meeting_id, stream_event)
        logger.debug(f"Событие отправлено в meeting {meeting_id}: {stream_event['type']}")
    
    def _to_stream_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразовать внутреннее событие в StreamEvent"""
        event_type = event.get("type", "unknown")
        
        if event_type == "agent_message":
            return {
                "type": "chat_message",
                "payload": {
                    "id": event.get("message_id", f"msg_{datetime.now().timestamp()}"),
                    "run_id": event.get("run_id"),
                    "agent_id": event.get("agent_id"),
                    "role": event.get("role", "assistant"),
                    "content": event.get("content"),
                    "created_at": event.get("timestamp", datetime.now().isoformat()),
                    "reply_to": event.get("reply_to")
                }
            }
        
        elif event_type == "participant_status":
            return {
                "type": "participant_updated", 
                "payload": {
                    "agent_id": event.get("agent_id"),
                    "status": event.get("status"),
                    "role": event.get("role")
                }
            }
        
        elif event_type == "tool_execution":
            return {
                "type": "tool_call",
                "payload": {
                    "thread_id": event.get("thread_id"),
                    "status": event.get("status"),
                    "tool_id": event.get("tool_id"),
                    "agent_id": event.get("agent_id"),
                    "args_masked": event.get("args_masked", {}),
                    "progress": event.get("progress", {})
                }
            }
        
        elif event_type == "artifact_created":
            return {
                "type": "artifact",
                "payload": {
                    "kind": event.get("artifact_type"),
                    "meeting_id": event.get("meeting_id"),
                    "page_id": event.get("external_ref"),
                    "url": event.get("url"),
                    "summary": event.get("summary"),
                    "created_at": event.get("timestamp", datetime.now().isoformat())
                }
            }
        
        elif event_type == "run_status":
            return {
                "type": "run_status",
                "payload": {
                    "run_id": event.get("run_id"),
                    "status": event.get("status"),
                    "meeting_id": event.get("meeting_id")
                }
            }
        
        else:
            # Неизвестный тип события
            return {
                "type": "unknown",
                "payload": event
            }
    
    async def emit_event(self, event: Dict[str, Any]):
        """Добавить событие в очередь для обработки"""
        await self._event_queue.put(event)
    
    async def stop_processing(self):
        """Остановить обработку событий"""
        self._is_processing = False
        logger.info("Остановлена обработка XIO событий")


# Глобальные экземпляры
connection_manager = WSConnectionManager()
event_broker = XIOEventBroker(connection_manager) 