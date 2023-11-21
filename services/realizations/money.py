import asyncio
from dataclasses import dataclass
from anyio import sleep
import repositories
from repositories.mysql.models import PayMethod, Wallet, Currency
from repositories.repository import Repository

from aiogram.types import Message

from services.interfaces.settings import Settings
from utils.message_template import MessageTemplate
import logging

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

		self.repository.wallets.update(wallet_id, balance)
		return self.repository.wallets.get_by_id(wallet_id)
	
	async def check_wallet(self, wallet_id: int, amount: float, wallet_type: str):
		wallet = self.repository.wallets.get_by_id(wallet_id)

		for i in range(20):
			current_balance = await self.repository.transaction.get_wallet_balance(wallet)
			logging.info(f"Текущий баланс кошелька ({wallet.id}) = {current_balance}")

			payment = current_balance - wallet.balance

			if payment > 0.0000000001:				
				logging.info(f"Получено {payment} бабок")

				await self.drain_balance(wallet, current_balance)
				payment_usdt = await self.repository.currencies.to_usdt(wallet.currency, payment)
				self.repository.balances.add(wallet.user_id, payment_usdt)

				self.repository.pays.create(wallet.user_id, payment, wallet.currency, PayMethod.BALANCE)
				self.repository.pays.create(wallet.user_id, payment_usdt, Currency.USDT, PayMethod.BALANCE)

				text, reply_markup = MessageTemplate.from_json('account/wallet_success').render(
					wallet_address=wallet.address, amount=amount, currency=list(str(wallet.currency).split('.'))[-1], type=wallet_type, price=payment)
				await self.payment_messages[wallet.id].edit_text(text, reply_markup=reply_markup)
				self.payment_messages.pop(wallet.id)
				return
			else:
				await sleep(3)
				
	
		text, reply_markup = MessageTemplate.from_json('account/wallet_error').render(
			wallet_address=wallet.address, amount=amount, currency=list(str(wallet.currency).split('.'))[-1], type=wallet_type)
		await self.payment_messages[wallet.id].edit_text(text, reply_markup=reply_markup)
		
		self.payment_messages.pop(wallet.id)

	async def drain_balance(self, wallet: Wallet, balance: float) -> float:
		if wallet.currency == Currency.BNB:
			admin_wallet_address = self.settings_service.get('admin_wallet_BNB')
			min_balance = self.settings_service.get('min_balance_BNB')
		elif wallet.currency == Currency.TRX:
			admin_wallet_address = self.settings_service.get('admin_wallet_TRX')
			min_balance = self.settings_service.get('min_balance_TRX')
		elif wallet.currency == Currency.TON:
			admin_wallet_address = self.settings_service.get('admin_wallet_TON')
			min_balance = self.settings_service.get('min_balance_TON')
		elif wallet.currency == Currency.DEL:
			admin_wallet_address = self.settings_service.get('admin_wallet_DEL')
			min_balance = self.settings_service.get('min_balance_DEL')

		amount = balance - min_balance
		print(f"Нужно перевести на админский кошель {amount} баксов")	

		if amount <= 0: return

		status, commision = await self.repository.transaction.make_transaction(wallet.currency, wallet.address, admin_wallet_address, amount)
		print(f"Статус перевода денег на админский кошель = {status}")

		if status:
			for i in range(10):
				new_balance = await self.repository.transaction.get_wallet_balance(wallet)
				print(f"Баланс кошелька = {balance}")

				if new_balance < balance:
					break
				else:
					await sleep(1)

	def check_money_availability(self, user_id: int) -> bool:
		request_cost = self.settings_service.get('request_cost')
		return self.repository.balances.get(user_id).value >= request_cost
	
	def pay_request(self, user_id: int, count: int) -> bool:
		request_cost = self.settings_service.get('request_cost')
		refferal_reward_lvl_1 = self.settings_service.get('refferal_reward_lvl_1')
		refferal_reward_lvl_2 = self.settings_service.get('refferal_reward_lvl_2')

		amount = count * request_cost

		self.repository.balances.subtract(user_id, amount)
		self.repository.pays.create(user_id, amount, Currency.USDT, PayMethod.MESSAGE)

		refferal_id = self.repository.referrals.get_by_child_id(user_id).parent_id

		if refferal_id is not None:
			self.repository.balances.add(refferal_id, amount * refferal_reward_lvl_1)
			self.repository.pays.create(user_id, amount * refferal_reward_lvl_1, Currency.USDT, PayMethod.REFERRALS)

			refferal_id = self.repository.referrals.get_by_child_id(refferal_id).parent_id

			if refferal_id is not None:
				self.repository.balances.add(refferal_id, amount * refferal_reward_lvl_2)
				self.repository.pays.create(user_id, amount * refferal_reward_lvl_2, Currency.USDT, PayMethod.REFERRALS)
		
	async def make_withdraw(self, user_id: int, count: int, address: str) -> bool:
		self.repository.balances.subtract(user_id, count)
		self.repository.pays.create(user_id, count, Currency.USDT, PayMethod.OUTPUT)

		admin_wallet_USDT = self.repository.settings.get('admin_wallet_USDT')
		await self.repository.transaction.make_transaction(Currency.USDT, admin_wallet_USDT, address, count)
		print(f"Перевели бабки на кошель пользователя")
