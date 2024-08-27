from abc import ABCMeta, abstractmethod


class Phone:
	def __init__(self, ):
		...

	async def create_call(self, from_: str, to: str):
		...

	async def get_available_numbers(self):
		...

	async def choose_number(self):
		...

