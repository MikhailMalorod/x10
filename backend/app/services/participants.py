"""
Сервис для работы с участниками консилиума
"""

from typing import List, Optional, Dict, Any
from app.models.participants import (
    Participant,
    ParticipantRole,
    ParticipantStatus,
    ToolBadge,
    ParticipantUpdate,
    SpeakingOrder
)

class ParticipantService:
    """Сервис для работы с участниками"""
    
    def __init__(self):
        # TODO: Заменить на реальное хранилище
        self._participants: Dict[str, Participant] = {}
        self._speaking_orders: Dict[str, SpeakingOrder] = {}
        
    def create_participant(self,
                         agent_id: str,
                         meeting_id: str,
                         role: ParticipantRole,
                         name: str,
                         model: Optional[str] = None,
                         tool_badges: Optional[List[ToolBadge]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Participant:
        """Создает нового участника"""
        
        participant = Participant(
            agent_id=agent_id,
            meeting_id=meeting_id,
            role=role,
            name=name,
            model=model,
            tool_badges=tool_badges or [],
            metadata=metadata or {}
        )
        
        self._participants[agent_id] = participant
        return participant
    
    def get_participant(self, agent_id: str) -> Optional[Participant]:
        """Получает участника по ID"""
        return self._participants.get(agent_id)
    
    def get_participants(self, meeting_id: str) -> List[Participant]:
        """Получает всех участников встречи"""
        return [
            p for p in self._participants.values()
            if p.meeting_id == meeting_id
        ]
    
    def update_participant(self,
                         agent_id: str,
                         update: ParticipantUpdate) -> Optional[Participant]:
        """Обновляет статус участника"""
        participant = self._participants.get(agent_id)
        if not participant:
            return None
            
        participant.status = update.status
        if update.metadata:
            participant.metadata.update(update.metadata)
            
        return participant
    
    def create_speaking_order(self,
                            meeting_id: str,
                            participants: List[Participant]) -> SpeakingOrder:
        """Создает порядок выступления участников"""
        
        # Сортируем по ролям: модератор -> эксперты -> хронист -> интегратор
        role_order = {
            ParticipantRole.MODERATOR: 0,
            ParticipantRole.EXPERT: 1,
            ParticipantRole.SCRIBE: 2,
            ParticipantRole.INTEGRATOR: 3,
            ParticipantRole.USER: 4
        }
        
        sorted_participants = sorted(
            participants,
            key=lambda p: (role_order[p.role], p.agent_id)
        )
        
        order = [p.agent_id for p in sorted_participants]
        
        speaking_order = SpeakingOrder(
            meeting_id=meeting_id,
            current_speaker=order[0] if order else None,
            next_speaker=order[1] if len(order) > 1 else None,
            order=order
        )
        
        self._speaking_orders[meeting_id] = speaking_order
        
        # Обновляем статусы участников
        if order:
            self.update_participant(
                order[0],
                ParticipantUpdate(status=ParticipantStatus.SPEAKING)
            )
            if len(order) > 1:
                self.update_participant(
                    order[1],
                    ParticipantUpdate(status=ParticipantStatus.NEXT)
                )
        
        return speaking_order
    
    def get_speaking_order(self, meeting_id: str) -> Optional[SpeakingOrder]:
        """Получает текущий порядок выступления"""
        return self._speaking_orders.get(meeting_id)
    
    def next_speaker(self, meeting_id: str) -> Optional[SpeakingOrder]:
        """Переключает на следующего спикера"""
        speaking_order = self._speaking_orders.get(meeting_id)
        if not speaking_order or not speaking_order.order:
            return None
            
        # Находим индекс текущего спикера
        current_idx = speaking_order.order.index(speaking_order.current_speaker)
        
        # Определяем следующего спикера
        next_idx = (current_idx + 1) % len(speaking_order.order)
        after_next_idx = (next_idx + 1) % len(speaking_order.order)
        
        # Обновляем статусы
        if speaking_order.current_speaker:
            self.update_participant(
                speaking_order.current_speaker,
                ParticipantUpdate(status=ParticipantStatus.WAITING)
            )
            
        speaking_order.current_speaker = speaking_order.order[next_idx]
        speaking_order.next_speaker = speaking_order.order[after_next_idx]
        
        # Если сделали полный круг, увеличиваем номер раунда
        if next_idx == 0:
            speaking_order.round += 1
            
        # Обновляем статусы новых спикеров
        self.update_participant(
            speaking_order.current_speaker,
            ParticipantUpdate(status=ParticipantStatus.SPEAKING)
        )
        self.update_participant(
            speaking_order.next_speaker,
            ParticipantUpdate(status=ParticipantStatus.NEXT)
        )
        
        return speaking_order

# Глобальный экземпляр сервиса
participant_service = ParticipantService() 