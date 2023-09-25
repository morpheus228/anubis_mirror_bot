from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..interfaces import Clients
from .models import Client

import pyrogram


class ClientsMYSQL(Clients):
    def __init__(self, engine):
        self.engine = engine
        
    def create(self, client: pyrogram.client.Client, phone_number: str, session_string: str) -> Client:
        with Session(self.engine) as session:
            client = Client(api_id=client.api_id,
                            api_hash=client.api_hash,
                            phone_number=phone_number,
                            name=client.name,
                            session_string=session_string,
                            requests_balance=100)
            
            session.add(client)
            session.commit()
            return client
    
    def get_by_info(self, api_id: int, api_hash: str, phone_number: str) -> Client|None:
        with Session(self.engine) as session:
            return session.query(Client).filter(
                 and_(Client.api_id == api_id,
                      Client.api_hash == api_hash,
                      Client.phone_number == phone_number)).first()
    
    def get_by_name(self, name: str) -> Client|None:
        with Session(self.engine) as session:
            return session.query(Client).get(name)
        
    def update_by_name(self, name: str, **kwargs) -> Client:
        client = self.get_by_name(name)

        with Session(self.engine) as session:
            for attr, value in kwargs.items():
                client.__setattr__(attr, value)
        
        session.add(client)
        session.commit()
        return client

    def get_available(self) -> Client|None:
        with Session(self.engine) as session:
            return session.query(Client).filter(
                and_(Client.is_used_by == None, 
                     Client.requests_balance > 0)).first()
    
    def clear(self):
        with Session(self.engine) as session:
            clients = session.query(Client).all()
            for client in clients:
                client.is_used_by = None
                session.add(client)
            
            session.commit()
    
    def get(self) -> list[Client]:
        with Session(self.engine) as session:
            return session.query(Client).all()

        