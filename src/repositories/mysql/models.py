import enum
from sqlalchemy import BigInteger, String, Column, DateTime, ForeignKey, Boolean, Integer, Text, Float, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'

    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_replay = Column(Boolean())
    status = Column(Boolean())
    created_at = Column(DateTime(), default=datetime.utcnow)


class Referral(Base):
    __tablename__ = 'Referrals'

    child_id = Column(BigInteger, ForeignKey('Users.id'), primary_key=True)
    parent_id = Column(BigInteger, ForeignKey('Users.id'), nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow)
    

class WalletType(enum.Enum):
    TON = "ton"
    USDT_BEP20 = "usdt_bep20"
    DEL = 'del'
    USDT_TRX20 = "usdt_trx20"

class Wallet(Base):
    __tablename__ = 'Wallets'

    user_id = Column(BigInteger, ForeignKey('Users.id'), primary_key=True)
    type = Column(Enum(WalletType))
    balance = Column(Float)
    addresse = Column(String(100))
    created_at = Column(DateTime(), default=datetime.utcnow)


class Currency(enum.Enum):
    RUB = "rub"
    TON = "ton"
    DEL = 'del'
    USDT = "usdt"

class PayMethod(enum.Enum):
    BALANCE = "balance"
    REFERRALS = "referrals"

class Pays(Base):
    __tablename__ = 'Pays'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('Users.id'))
    price = Column(Float)
    currency = Column(Enum(Currency))
    method = Column(Enum(PayMethod))
    status = Column(Integer)
    paid_at = Column(DateTime())
    created_at = Column(DateTime(), default=datetime.utcnow)
    

class Client(Base):
    __tablename__ = 'Clients'

    name = Column(String(50), primary_key=True)
    api_id = Column(BigInteger)
    api_hash = Column(String(100))
    phone_number = Column(String(50))
    session_string = Column(String(1024))

    is_used_by = Column(BigInteger, ForeignKey('Users.id'), nullable=True)
    
    remains_amount = Column(BigInteger, nullable=True)

    created_at = Column(DateTime(), default=datetime.utcnow)