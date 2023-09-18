from sqlalchemy.orm import Session

from ..interfaces import Settings
from .models import Setting


class SettingsMYSQL(Settings):
    def __init__(self, engine):
        self.engine = engine
    
    def get(self) -> Setting:
        with Session(self.engine) as session:
            return session.query(Setting).first()
    
    def create(self, setting: Setting) -> Setting:
        with Session(self.engine) as session:
            session.add(setting)
            session.commit()
            return setting