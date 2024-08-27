import typing
from pydantic import BaseModel
from enum import Enum


class STT:
	def __init__(self, provider: typing.Literal['deepgram'], api_key: str):
		self.provider = provider

