from sqlalchemy.orm import Session

from ..interfaces import Referrals
from .models import Referral


class ReferralsMYSQL(Referrals):
    def __init__(self, engine):
        self.engine = engine
    
    def get_by_child_id(self, child_id: int) -> Referral|None:
        with Session(self.engine) as session:
            return session.query(Referral).filter(Referral.child_id == child_id).first()
    
    def create(self, child_id: int, parent_id: int) -> Referral:
        with Session(self.engine) as session:
            referral = Referral(child_id=child_id, parent_id=parent_id)
            session.add(referral)
            session.commit()
            return referral
		