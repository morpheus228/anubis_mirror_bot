import enum
from sqlalchemy import BigInteger, String, Column, DateTime, ForeignKey, Boolean, Integer, Text, Float, Enum, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_replay = Column(Boolean())
    status = Column(Boolean())
    created_at = Column(DateTime(), default=datetime.utcnow)


class Referral(Base):
    __tablename__ = 'referrals'

    child_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    parent_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow)


class Currency(enum.Enum):
    USDT = "usdt"
    TON = "ton"
    DEL = 'del'
    BNB = 'bnb'
    TRX = "trx"

class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    currency = Column(Enum(Currency))
    balance = Column(Float)
    address = Column(String(100))
    created_at = Column(DateTime(), default=datetime.utcnow)


class Balance(Base):
    __tablename__ = 'balances'
    
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    value = Column(Float)


class PayMethod(enum.Enum):
    OUTPUT = "output"
    BALANCE = "balance"
    REFERRALS = "referrals"
    MESSAGE = "message"

class Pay(Base):
    __tablename__ = 'pays'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    price = Column(Float)
    currency = Column(Enum(Currency))
    method = Column(Enum(PayMethod))
    status = Column(Integer)
    description = Column(String(255))
    paid_at = Column(DateTime(), default=datetime.utcnow)
    created_at = Column(DateTime(), default=datetime.utcnow)
    

class Client(Base):
    __tablename__ = 'clients'

    name = Column(String(50), primary_key=True)
    api_id = Column(BigInteger)
    api_hash = Column(String(100))
    phone_number = Column(String(50))
    session_string = Column(String(1024))

    is_used_by = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    
    requests_balance = Column(BigInteger, nullable=True)

    created_at = Column(DateTime(), default=datetime.utcnow)


class Setting(Base):
    __tablename__ = 'settings'

    name = Column(String(250), primary_key=True)
    name_user = Column(String(250))
    value = Column(JSON())


class SendMessage(Base):
    __tablename__ = 'send_message'

    id = Column(String(50), primary_key=True)
    text = Column(Text())
    type = Column(String(15))
    send = Column(Integer)
    date_create = Column(DateTime(), default=datetime.utcnow)