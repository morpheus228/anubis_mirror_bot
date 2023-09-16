from sqlalchemy import create_engine

from config import MYSQLConfig

from .referrals import ReferralsMYSQL
from .clients import ClientsMYSQL
from .users import UsersMYSQL

from .models import Base


def get_engine(config: MYSQLConfig):
	engine_str = f"mysql+pymysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"
	engine = create_engine(engine_str)
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	return engine
