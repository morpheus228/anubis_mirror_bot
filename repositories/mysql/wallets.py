from sqlalchemy.orm import Session

from ..interfaces import Wallets
from .models import Wallet, Currency


class WalletsMYSQL(Wallets):
    def __init__(self, engine):
        self.engine = engine
        
    def create(self, user_id: int, currency: Currency, address: str, balance: float = 0):
        with Session(self.engine) as session:
            wallet = Wallet(user_id=user_id, currency=currency, address=address, balance=balance)
            session.add(wallet)
            session.commit()
    
    def get_by_user(self, user_id: int, currency: Currency) -> int:
        with Session(self.engine) as session:
            return session.query(Wallet.id).filter(Wallet.user_id == user_id, Wallet.currency == currency).first()[0]
    
    def get_by_id(self, wallet_id: int) -> Wallet:
        with Session(self.engine) as session:
            return session.query(Wallet).get(wallet_id)
    
    def update(self, wallet_id: int, balance: float) -> Wallet:
        with Session(self.engine) as session:
            wallet = session.query(Wallet).get(wallet_id)
            wallet.balance = balance
            session.commit()
        