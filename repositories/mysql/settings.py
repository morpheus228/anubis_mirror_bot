from sqlalchemy.orm import Session

from ..interfaces import Settings
from .models import Setting


class SettingsMYSQL(Settings):
    def __init__(self, engine):
        self.engine = engine
    
    def get(self, name: str) -> Setting:
        with Session(self.engine) as session:
            return session.query(Setting).get(name)
    
    def create(self, name: str, name_user: str, value) -> Setting:
        with Session(self.engine) as session:
            session.add(Setting(name=name, name_user=name_user, value=value))
            session.commit()
