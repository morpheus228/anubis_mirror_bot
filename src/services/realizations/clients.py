# import repositories

import repositories
from ..interfaces import Clients

from pyrogram.client import Client
from pyrogram.types import SentCode

from utils import generate_str


class ClientsService(Clients):
	def __init__(self, repository: repositories.Clients):
		self.repository: repositories.Clients = repository

	async def check_uniqueness(self, api_id: int, api_hash: str, phone_number: str) -> bool:
		return self.repository.get_by_info(api_id, api_hash, phone_number) is None

	async def request_sms_code(self, api_id: int, api_hash: str, phone_number: str) -> tuple[Client, SentCode]:
		session_name = generate_str(15)

		client = Client(session_name, api_id, api_hash, in_memory=True)
		await client.connect()
		
		return client, await client.send_code(phone_number)  

	async def create(self, client: Client, phone_number: str, code_info: SentCode, sms_code: str) -> str:
		await client.sign_in(phone_number, code_info.phone_code_hash, sms_code)
		await client.send_message("me", "This account has been added to <b>Pyrogram!</b>")
		session_string = await client.export_session_string()
		self.repository.create(client, phone_number, session_string)
		return client.name
	
	def get(self, user_id: int) -> Client|None:
		client = self.repository.get_available()

		if client is None: 
			return None
		
		self.repository.update_by_name(client.name, is_used_by=user_id)
		return Client(client.name, session_string=client.session_string)
	
	def give(self, name: str, session_string: str):
		self.repository.update_by_name(name, is_used_by=None, session_string=session_string)