from sqlalchemy import create_engine

from config import MYSQLConfig

from .referrals import ReferralsMYSQL
from .clients import ClientsMYSQL
from .users import UsersMYSQL
from .settings import SettingsMYSQL
from .balances import BalancesMYSQL
from .wallets import WalletsMYSQL
from .transactions import TransactionsAPI
from .currencies import CurrenciesAPI
from .pays import PaysMYSQL

from .models import Base


def get_engine(config: MYSQLConfig):
	engine_str = f"mysql+pymysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"
	engine = create_engine(engine_str)
	return engine
