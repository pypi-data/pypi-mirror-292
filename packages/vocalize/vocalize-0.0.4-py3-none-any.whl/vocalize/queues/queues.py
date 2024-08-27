import asyncio
import typing


class ElevenLabsOutputQueueDict(typing.TypedDict):
    """
    Type definition for the Queue that receives from the TTS and sends to Output
    """
    text: str | None
    audio: str | None


ElevenLabsOutputQueue: typing.TypeAlias = asyncio.Queue[ElevenLabsOutputQueueDict | None]

