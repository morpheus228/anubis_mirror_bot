from sqlalchemy.orm import Session

from ..interfaces import Queue
from .models import QueuePosition


class QueueMYSQL(Queue):
    def __init__(self, engine):
        self.engine = engine
        
    def create(self, user_id: int):
        with Session(self.engine) as session:
            position = QueuePosition(user_id=user_id)
            session.add(position)
            session.commit()
    
    def get(self) -> QueuePosition|None:
        with Session(self.engine) as session:
            position = session.query(QueuePosition).order_by(QueuePosition.created_at).first()

            if position is not None:
                session.delete(position)
                session.commit()

            return position
    
    def get_count(self) -> int:
        with Session(self.engine) as session:
            return session.query(QueuePosition).count()
        