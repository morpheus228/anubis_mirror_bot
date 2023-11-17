from sqlalchemy.orm import Session

from ..interfaces import Balances
from .models import Balance


class BalancesMYSQL(Balances):
    def __init__(self, engine):
        self.engine = engine
        
    def create(self, user_id: int, value: float = 0):
        with Session(self.engine) as session:
            balance = Balance(user_id=user_id, value=value)
            session.add(balance)
            session.commit()
    
    def get(self, user_id: int) -> Balance|None:
        with Session(self.engine) as session:
            return session.query(Balance).get(user_id)
    
    def update(self, user_id: int, value: float):
        with Session(self.engine) as session:
            balance = session.query(Balance).get(user_id)
            balance.value = value
            session.commit()
        
    def add(self, user_id: int, value: float):
        with Session(self.engine) as session:
            balance = session.query(Balance).get(user_id)
            balance.value += value
            session.commit()
    
    def subtract(self, user_id: int, value: float):
        with Session(self.engine) as session:
            balance = session.query(Balance).get(user_id)
            balance.value -= value
            session.commit()
        