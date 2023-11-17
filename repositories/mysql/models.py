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

    child_id = Column(BigInteger, ForeignKey('Users.id', ondelete='CASCADE'), primary_key=True)
    parent_id = Column(BigInteger, ForeignKey('Users.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow)


class Currency(enum.Enum):
    USDT = "usdt"
    TON = "ton"
    DEL = 'del'
    BNB = 'bnb'
    TRX = "trx"

class Wallet(Base):
    __tablename__ = 'Wallets'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('Users.id', ondelete='CASCADE'))
    currency = Column(Enum(Currency))
    balance = Column(Float)
    address = Column(String(100))
    created_at = Column(DateTime(), default=datetime.utcnow)


class Balance(Base):
    __tablename__ = 'Balances'
    
    user_id = Column(BigInteger, ForeignKey('Users.id', ondelete='CASCADE'), primary_key=True)
    value = Column(Float)


class PayMethod(enum.Enum):
    OUTPUT = "output"
    BALANCE = "balance"
    REFERRALS = "referrals"
    MESSAGE = "message"

class Pay(Base):
    __tablename__ = 'Pays'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('Users.id', ondelete='CASCADE'))
    price = Column(Float)
    currency = Column(Enum(Currency))
    method = Column(Enum(PayMethod))
    status = Column(Integer)
    paid_at = Column(DateTime(), default=datetime.utcnow)
    created_at = Column(DateTime(), default=datetime.utcnow)
    

class Client(Base):
    __tablename__ = 'Clients'

    name = Column(String(50), primary_key=True)
    api_id = Column(BigInteger)
    api_hash = Column(String(100))
    phone_number = Column(String(50))
    session_string = Column(String(1024))

    is_used_by = Column(BigInteger, ForeignKey('Users.id', ondelete='CASCADE'), nullable=True)
    
    requests_balance = Column(BigInteger, nullable=True)

    created_at = Column(DateTime(), default=datetime.utcnow)


class Setting(Base):
    __tablename__ = 'Settings'

    id = Column(BigInteger, primary_key=True)

    extra_charge = Column(Float)
    request_cost = Column(Float)

    refferal_reward_lvl_1 = Column(Float)
    refferal_reward_lvl_2 = Column(Float)

    # commission_input_DEL = Column(Float)
    # commission_input_TON = Column(Float)
    # commission_input_BNB = Column(Float)
    # commission_input_TRX = Column(Float)

    # commission_output_BNB = Column(Float)
    # commission_output_DEL = Column(Float)
    # commission_output_TON = Column(Float)
    # commission_output_TRX = Column(Float)

    commissio_output_USDT = Column(Float)

    admin_wallet_BNB = Column(String(1024))
    admin_wallet_DEL = Column(String(1024))
    admin_wallet_TON = Column(String(1024))
    admin_wallet_TRX = Column(String(1024))
    admin_wallet_USDT = Column(String(1024))

    min_balance_BNB  = Column(Float)
    min_balance_DEL = Column(Float)
    min_balance_TON = Column(Float)
    min_balance_TRX = Column(Float)

    min_output_USDT = Column(Float)
    max_output_USDT = Column(Float)

    updated_at = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)