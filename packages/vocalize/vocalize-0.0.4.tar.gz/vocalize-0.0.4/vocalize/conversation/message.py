import typing
from pydantic import BaseModel, Field
from datetime import datetime
import datetime as dt
import uuid

from .role import Role

# generic typing class for storing message metadata
MetadataType = typing.TypeVar("MetadataType")

    
    


class Message(BaseModel, typing.Generic[MetadataType]):
	role: Role
	content: str
	uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
	created_at: datetime = Field(default_factory=lambda: datetime.now(tz=dt.timezone.utc))
	metadata: MetadataType
	start_at: datetime = Field(default_factory=lambda: datetime.now(tz=dt.timezone.utc))
	finished_at: datetime | None = Field(default=None)

	def __getitem__(self, item: str):
		as_dict = self.model_dump()
		return str(as_dict[item])

	def __str__(self):
		return f"{str(self.role)}{self.content}"
