import asyncio
from abc import ABCMeta, abstractmethod


class FlowStep(metaclass=ABCMeta):
	"""
	An abstract base class for all flow steps. This ABC dictates the common methods that must be used
	by all the steps in the flow.
	"""

	def __init__(self, ) -> None:
		self.input_queue = None
		self.output_queue = None



	@abstractmethod
	async def start(self, ) -> None:
		"""
		Starts the flow step and should terminate once the call is disconnected
		:return:
		:rtype: None
		"""
		...
