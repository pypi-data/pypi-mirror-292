from pydantic import BaseModel, Field
import typing
import asyncio
from ..conversation.role import Role, Roles
from ..conversation.message import Message
import abc

MessageMetadataType = typing.TypeVar("MessageMetadataType")

class ContinuedMessage(Message[MessageMetadataType]):
    original_message: Message[MessageMetadataType]
    continuation_text: str


# * Will maybe add these later.
on_add_conversation_type = typing.Callable[[Message[MessageMetadataType] | ContinuedMessage[MessageMetadataType]], None]

T = typing.TypeVar("T")
Y = typing.TypeVar("Y")


class ConversationHooks(BaseModel, typing.Generic[MessageMetadataType]):
    ON_ADD_MESSAGE: list[
        "ConversationHook[typing.Callable[[Message[MessageMetadataType] | ContinuedMessage[MessageMetadataType]], typing.Coroutine[typing.Any, typing.Any, None]]]"
    ] = Field(default_factory=list)


class ConversationHook(typing.Generic[T], BaseModel):
    """
    A class to add a hook for the conversation. This is useful for adding additional functionality to the conversation
    without modifying the conversation itself. This is useful for adding logging, database interactions, or other
    side effects to the conversation.
    """

    hook_function: T


class CustomConversation(BaseModel, abc.ABC, typing.Generic[MessageMetadataType]):
    """
    Create a custom conversation. It must implement the following methods:

    format: format the conversation to send to the LLM
    """

    internal_messages: typing.List[Message[MessageMetadataType]] = Field(default=[], alias="_messages")
    roles: Roles
    debug: bool = False
    metadata: typing.Dict[str, typing.Any] = Field(default={})
    conversation_hooks: ConversationHooks[MessageMetadataType] = Field(default_factory=ConversationHooks)

    

    @property
    def messages(self) -> typing.List[Message[MessageMetadataType]]:
        return self.internal_messages



    async def _handle_on_add_message_hooks(self, message: "Message[MessageMetadataType] | ContinuedMessage[MessageMetadataType]"):
        hook_tasks: list[asyncio.Task[None]] = []
        for conversation_hook in self.conversation_hooks.ON_ADD_MESSAGE:
            hook_tasks.append(
                asyncio.create_task(
                    conversation_hook.hook_function(message)
                )
            )
        await asyncio.gather(*hook_tasks)

            

    async def add_message(self, role: Role, content: str, metadata: MessageMetadataType):
        """
        First checks if the message is a continuation of the previous message and either creates a new message or updates
        the existing one. It identifies if it's a continuation by seeing if the provided role matches the role
        of the last message in the conversation. The thinking goes: Conversations are turned based and until
        the speaker changes, it's still the same speaker's turn and thus, a continuation of the same message.
        :param role:
        :type role:
        :param content:
        :type content:
        :return:
        :rtype:
        """
        if self.is_continuation(role):
            # ContinuedMessage is a class that extends Message and adds a few more fields to it. It is used for the 
            # conversation hooks to identify if the message is a new message or a continuation of the previous message.
            continued_message = ContinuedMessage(
                content=f"{self.messages[-1].content}{content}",
                metadata=metadata if metadata else self.messages[-1].metadata,
                created_at=self.messages[-1].created_at,
                uuid=self.messages[-1].uuid,
                role=self.messages[-1].role,
                original_message=self.messages[-1],
                continuation_text=content,
            )
            await self._handle_on_add_message_hooks(continued_message)
            self.messages[-1].content += f"{content}"
            if metadata:
                self.messages[-1].metadata = metadata
            return self.messages[-1]

        new_message = Message[MessageMetadataType](role=role, content=content, metadata=metadata)
        await self._handle_on_add_message_hooks(new_message)
        self.messages.append(new_message)
        return new_message

    def is_continuation(self, role: Role) -> bool:
        """
        Check the last message in the conversation, if the role is the same. Then it is a continuation message.
        Continuations happen when we are receiving LLM responses in chunks or in streams.
        :param role: The role of the content to add
        :type role: Role
        :return: Whether this is a continuation message
        :rtype: bool
        """
        if len(self.messages) == 0:
            return False
        if self.messages[-1].role is role:
            if self.debug:
                print("is continuation CONFIRMED")
            return True
        return False

    @property
    def assistant_prompt(self):
        prompt = self.format()
        assert prompt is not None, (
            "We tried to format the conversation but it returned None. "
            "Double check you are returning the formatted conversation in the `.format()` method"
        )

        if self.debug:
            print(f"assistant prompt: {prompt}")
        return prompt

    @abc.abstractmethod
    def format(self) -> str:
        raise NotImplementedError(
            "CustomConversation subclass must implement format() method"
        )

    # @property
    # def assistant_prompt(self):
    #     raise NotImplementedError('CustomConversation subclass must implement assistant_prompt as a @property')


class Conversation(CustomConversation[MessageMetadataType]):
    """
    Handles the conversation through adding messages, and formatting them.
    """

    @staticmethod
    def default_roles() -> Roles:
        user_role = Role(name="user", replace_with="USER:")
        system_role = Role(name="system", replace_with="SYSTEM:")
        assistant_role = Role(name="assistant", replace_with="ASSISTANT:")
        return Roles(user=user_role, system=system_role, assistant=assistant_role)

    @property
    def assistant_prompt(self):
        prompt = self.format()
        role: Role = self.roles.assistant
        prompt += f"{str(role)}"
        return prompt

    def format(self) -> str:
        """
        Convert the conversation and all of its messages into the final prompt that will be fed into an LLM for completion.
        :return:
        :rtype:
        """
        prompt = ""
        for message in self.messages:
            prompt += f"{str(message)}\n\n"
        return prompt
