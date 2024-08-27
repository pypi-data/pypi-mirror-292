import asyncio
from dataclasses import dataclass


class IsCallConnected(asyncio.Event):
    """The asyncio.Event() that represents whether the call is still connected or not.

    This will be set -- using .set() -- when the call is first connected and will be unset -- using .clear() -- when the user hangs up or the call is disconnected

    """

    def __init__(self):
        super().__init__()


@dataclass
class Events:
    """
    Holds all the asyncio.Events that steps in the flow may use
    """

    is_call_connected: IsCallConnected
    is_interrupted: asyncio.Event
    is_turn_complete: asyncio.Event
