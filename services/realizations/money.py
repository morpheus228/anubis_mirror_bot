import asyncio
from dataclasses import dataclass
from anyio import sleep
import repositories
from repositories.mysql.models import PayMethod, Wallet, Currency
from repositories.repository import Repository

from aiogram.types import Message

from services.interfaces.settings import Settings
from utils.message_template import MessageTemplate

from ..interfaces import Money


class MoneyService(Money):
	payment_messages: dict[int, Message] = {}

	def __init__(self, repository: Repository, settings_service: Settings):
		self.settings_service: Settings = settings_service
		self.repository: Repository = repository

	def get_user_balance(self, user_id: int) -> float|None:
		balance = self.repository.balances.get(user_id)
		if balance is None:
			return -1
		else:
			return balance.value
		
	async def get_user_wallet(self, user_id: int, currency: str) -> Wallet:
		wallet_id = self.repository.wallets.get_by_user(user_id, currency)

		wallet = self.repository.wallets.get_by_id(wallet_id)
		balance = await self.repository.transaction.get_wallet_balance(wallet)

		# balance = 99

		self.repository.wallets.update(wallet_id, balance)
		return self.repository.wallets.get_by_id(wallet_id)
	
	async def check_wallet(self, wallet_id: int, amount: float, wallet_type: str):
		wallet = self.repository.wallets.get_by_id(wallet_id)

		for i in range(30):
			current_balance = await self.repository.transaction.get_wallet_balance(wallet)

			# if i == 2:
			# 	current_balance = 100
			# else:
			# 	current_balance = 99

			payment = current_balance - wallet.balance

			if payment > 0:				
				await self.drain_balance(wallet, current_balance)
				payment_usdt = await self.repository.currencies.to_usdt(wallet.currency, payment)
				self.repository.balances.add(wallet.user_id, payment_usdt)

				self.repository.pays.create(wallet.user_id, payment, wallet.currency, PayMethod.BALANCE)
				self.repository.pays.create(wallet.user_id, payment_usdt, Currency.USDT, PayMethod.BALANCE)

				text, reply_markup = MessageTemplate.from_json('account/wallet_success').render(
					wallet_address=wallet.address, amount=amount, currency=list(str(wallet.currency).split('.'))[-1], type=wallet_type, price=payment)
				await self.payment_messages[wallet.id].edit_text(text, reply_markup=reply_markup)

				self.payment_messages.pop(wallet.id)
				break

			else:
				await sleep(10)
				
		else:
			text, reply_markup = MessageTemplate.from_json('account/wallet_error').render(
				wallet_address=wallet.address, amount=amount, currency=list(str(wallet.currency).split('.'))[-1], type=wallet_type)
			await self.payment_messages[wallet.id].edit_text(text, reply_markup=reply_markup)

	async def drain_balance(self, wallet: Wallet, balance: float) -> float:
		settings = self.settings_service.get()

		if wallet.currency == Currency.BNB:
			admin_wallet_address = settings.admin_wallet_BNB
			min_balance = settings.min_balance_BNB
		elif wallet.currency == Currency.TRX:
			admin_wallet_address = settings.admin_wallet_TRX
			min_balance = settings.min_balance_TRX
		elif wallet.currency == Currency.TON:
			admin_wallet_address = settings.admin_wallet_TON
			min_balance = settings.min_balance_TON
		elif wallet.currency == Currency.DEL:
			admin_wallet_address = settings.admin_wallet_DEL
			min_balance = settings.min_balance_DEL

		amount = balance - min_balance
		print(f"{amount} переводим на кошель админа")

		status, commision = await self.repository.transaction.make_transaction(wallet.type, wallet.address, admin_wallet_address, amount)
		if status:
			while True:
				balance = await self.repository.transaction.get_wallet_balance(wallet)
				if min_balance == balance:
					break
				else:
					await sleep(1)

	def check_money_availability(self, user_id: int) -> bool:
		settings = self.settings_service.get()
		return self.repository.balances.get(user_id).value >= settings.request_cost
	
	def pay_request(self, user_id: int, count: int) -> bool:
		settings = self.settings_service.get()
		amount = count * settings.request_cost

		self.repository.balances.subtract(user_id, amount)
		self.repository.pays.create(user_id, amount, Currency.USDT, PayMethod.MESSAGE)

		refferal_id = self.repository.referrals.get_by_child_id(user_id).parent_id

		if refferal_id is not None:
			self.repository.balances.add(refferal_id, amount * settings.refferal_reward_lvl_1)
			self.repository.pays.create(user_id, amount * settings.refferal_reward_lvl_1, Currency.USDT, PayMethod.REFERRALS)

			refferal_id = self.repository.referrals.get_by_child_id(refferal_id).parent_id

			if refferal_id is not None:
				self.repository.balances.add(refferal_id, amount * settings.refferal_reward_lvl_2)
				self.repository.pays.create(user_id, amount * settings.refferal_reward_lvl_2, Currency.USDT, PayMethod.REFERRALS)
		
	async def make_withdraw(self, user_id: int, count: int, address: str) -> bool:
		self.repository.balances.subtract(user_id, count)
		self.repository.pays.create(user_id, count, Currency.USDT, PayMethod.OUTPUT)

		settings = self.repository.settings.get()
		await self.repository.transaction.make_transaction(Currency.USDT, settings.admin_wallet_USDT, address, count)
		print(f"Перевели бабки на кошель пользователя")
