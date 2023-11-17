from sqlalchemy.orm import Session

from repositories.mysql.models import Currency, Pay, PayMethod


class PaysMYSQL:
    def __init__(self, engine):
        self.engine = engine
    
    def create(self, user_id: int, price: float, currency: Currency, method: PayMethod, status: int = 1):
        with Session(self.engine) as session:
            pay = Pay(user_id=user_id, price=price, currency=currency, method=method, status=status) 
            session.add(pay)
            session.commit()
		