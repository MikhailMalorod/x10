"""
Сервис для работы с сообщениями консилиума
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.messages import (
    Message,
    MessageThread,
    MessageRole,
    MessageType,
    DecisionMessage,
    TaskMessage,
    ToolCallMessage
)

class MessageService:
    """Сервис для работы с сообщениями"""
    
    def __init__(self):
        # TODO: Заменить на реальное хранилище
        self._messages: Dict[str, Message] = {}
        self._threads: Dict[str, MessageThread] = {}
        
    def create_message(self,
                      meeting_id: str,
                      run_id: str,
                      agent_id: str,
                      role: MessageRole,
                      content: str,
                      reply_to: Optional[str] = None,
                      thread_id: Optional[str] = None,
                      message_type: MessageType = MessageType.CHAT,
                      metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Создает новое сообщение"""
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        message = Message(
            id=message_id,
            meeting_id=meeting_id,
            run_id=run_id,
            agent_id=agent_id,
            role=role,
            type=message_type,
            content=content,
            created_at=datetime.now(),
            reply_to=reply_to,
            thread_id=thread_id,
            metadata=metadata or {}
        )
        
        self._messages[message_id] = message
        
        if thread_id:
            self._add_to_thread(message, thread_id)
            
        return message
    
    def create_decision_message(self,
                              meeting_id: str,
                              run_id: str,
                              agent_id: str,
                              content: str,
                              decision_id: str,
                              alternatives_count: int,
                              selected_option: str,
                              confidence: float,
                              thread_id: Optional[str] = None) -> DecisionMessage:
        """Создает сообщение о принятии решения"""
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        message = DecisionMessage(
            id=message_id,
            meeting_id=meeting_id,
            run_id=run_id,
            agent_id=agent_id,
            role=MessageRole.ASSISTANT,
            content=content,
            created_at=datetime.now(),
            thread_id=thread_id,
            metadata={
                "decision_id": decision_id,
                "alternatives_count": alternatives_count,
                "selected_option": selected_option,
                "confidence": confidence
            }
        )
        
        self._messages[message_id] = message
        
        if thread_id:
            self._add_to_thread(message, thread_id)
            
        return message
    
    def create_task_message(self,
                          meeting_id: str,
                          run_id: str,
                          agent_id: str,
                          content: str,
                          task_id: str,
                          priority: str,
                          assignee: str,
                          due_date: Optional[str] = None,
                          thread_id: Optional[str] = None) -> TaskMessage:
        """Создает сообщение о создании задачи"""
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        message = TaskMessage(
            id=message_id,
            meeting_id=meeting_id,
            run_id=run_id,
            agent_id=agent_id,
            role=MessageRole.ASSISTANT,
            content=content,
            created_at=datetime.now(),
            thread_id=thread_id,
            metadata={
                "task_id": task_id,
                "priority": priority,
                "assignee": assignee,
                "due_date": due_date
            }
        )
        
        self._messages[message_id] = message
        
        if thread_id:
            self._add_to_thread(message, thread_id)
            
        return message
    
    def create_tool_call_message(self,
                               meeting_id: str,
                               run_id: str,
                               agent_id: str,
                               content: str,
                               tool_id: str,
                               status: str,
                               args_masked: Dict[str, Any],
                               thread_id: Optional[str] = None) -> ToolCallMessage:
        """Создает сообщение о вызове инструмента"""
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        message = ToolCallMessage(
            id=message_id,
            meeting_id=meeting_id,
            run_id=run_id,
            agent_id=agent_id,
            role=MessageRole.TOOL,
            content=content,
            created_at=datetime.now(),
            thread_id=thread_id,
            metadata={
                "tool_id": tool_id,
                "status": status,
                "args_masked": args_masked
            }
        )
        
        self._messages[message_id] = message
        
        if thread_id:
            self._add_to_thread(message, thread_id)
            
        return message
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Получает сообщение по ID"""
        return self._messages.get(message_id)
    
    def get_messages(self,
                    meeting_id: str,
                    limit: int = 50,
                    offset: int = 0,
                    message_type: Optional[MessageType] = None) -> List[Message]:
        """Получает список сообщений встречи"""
        
        messages = [
            msg for msg in self._messages.values()
            if msg.meeting_id == meeting_id
            and (not message_type or msg.type == message_type)
        ]
        
        # Сортируем по времени создания
        messages.sort(key=lambda x: x.created_at)
        
        return messages[offset:offset + limit]
    
    def create_thread(self, meeting_id: str, metadata: Optional[Dict[str, Any]] = None) -> MessageThread:
        """Создает новую цепочку сообщений"""
        
        thread_id = f"thread_{uuid.uuid4().hex[:8]}"
        
        thread = MessageThread(
            thread_id=thread_id,
            meeting_id=meeting_id,
            metadata=metadata or {}
        )
        
        self._threads[thread_id] = thread
        return thread
    
    def get_thread(self, thread_id: str) -> Optional[MessageThread]:
        """Получает цепочку по ID"""
        return self._threads.get(thread_id)
    
    def get_threads(self, meeting_id: str) -> List[MessageThread]:
        """Получает все цепочки встречи"""
        return [
            thread for thread in self._threads.values()
            if thread.meeting_id == meeting_id
        ]
    
    def _add_to_thread(self, message: Message, thread_id: str):
        """Добавляет сообщение в цепочку"""
        thread = self._threads.get(thread_id)
        if not thread:
            thread = self.create_thread(message.meeting_id)
            self._threads[thread_id] = thread
        
        thread.messages.append(message)

# Глобальный экземпляр сервиса
message_service = MessageService() 