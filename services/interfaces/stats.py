from abc import ABC, abstractmethod
from attr import dataclass




@dataclass
class Stat:
	users_count: int
	busy_clients_count: int
	clients_count: int
	queue_size: int
	request_count: int


class Stats(ABC):
	@abstractmethod
	def get(self) -> Stat:
		pass