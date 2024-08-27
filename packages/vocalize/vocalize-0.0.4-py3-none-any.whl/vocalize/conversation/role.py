import typing
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import uuid


class RoleMetadata(BaseModel):
    participant_uuid: str | None

class CustomRole(BaseModel, ABC):
    name: str
    replace_with: str | None = Field(default=None)
    metadata: RoleMetadata = Field(default_factory=lambda: RoleMetadata(participant_uuid=None))
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @abstractmethod
    def __str__(self) -> typing.Any:
        raise NotImplementedError('CustomRole subclass must implement __str__ method')


class Role(CustomRole):

    def __str__(self):
        if self.replace_with:
            return self.replace_with
        return self.name


class Roles(BaseModel):
    system: Role
    assistant: Role
    user: Role
    additional_roles: typing.List[Role] = Field(default_factory=list)

    def add_role(self, role: Role):
        self.additional_roles.append(role)
