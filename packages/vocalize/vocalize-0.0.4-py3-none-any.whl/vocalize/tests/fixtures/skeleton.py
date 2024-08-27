import pytest
import asyncio
from vocalize.conversation import Conversation, Role, Roles
from vocalize.flow.events import Events, IsCallConnected
from vocalize.interrupter.interrupter import Interrupter
from .initialize import load_env


@pytest.fixture
@pytest.mark.asyncio
async def initialize_skeleton() -> tuple[Conversation, Events, asyncio.Queue, asyncio.Queue, Interrupter]:
    # from dotenv import load_dotenv
    # load_dotenv()
    user_role = Role(name="user")
    assistant_role = Role(name="assistant")
    system_role = Role(name="system")
    roles = Roles(assistant=assistant_role, system=system_role, user=user_role)

    conversation = Conversation(roles=roles)
    await conversation.add_message(
        role=system_role,
        content="You are a helpful assistant. Identify what the user needs and assist them with.",
    )
    is_call_connected = IsCallConnected()
    is_call_connected.set()
    is_interrupted = asyncio.Event()
    is_turn_complete = asyncio.Event()
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()


    events = Events(
        is_call_connected=is_call_connected,
        is_interrupted=is_interrupted,
        is_turn_complete=is_turn_complete
    )

    interrupter = Interrupter(
        debug=True,
        events=events,
        queues=[input_queue, output_queue],
        
    )
    return conversation, events, input_queue, output_queue, interrupter 
