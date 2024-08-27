from fastapi import WebSocket
import websockets
from websockets.client import WebSocketClientProtocol
import json
import asyncio
import typing
from abc import ABC, abstractmethod
from pydantic import BaseModel
from dataclasses import dataclass
from urllib.parse import urlencode
from loguru import logger
from websockets.legacy.client import Connect

from ..conversation import Role, Conversation
from ..conversation.conversation import Roles, CustomConversation
from ..flow import FlowStep
from collections.abc import Callable

from ..flow.events import Events
from ..interrupter.interrupter import Interrupter

OnOutput = Callable[["Deepgram", str], None]
OnInput = Callable[["Deepgram", str], None]


class DeepgramAlternativeWord(BaseModel):
    word: str
    start: float
    end: float
    confidence: float

class DeepgramChannelAlternative(BaseModel):
    transcript: str
    confidence: float
    words: list[DeepgramAlternativeWord]

class DeepgramChannel(BaseModel):
    alternatives: list[DeepgramChannelAlternative]

class DeepgramTranscription(BaseModel):
    type: str
    channel: DeepgramChannel
    channel_index: list[float]
    duration: float
    start: float
    is_final: bool
    speech_final: bool
    metadata: typing.Any
    from_finalize: bool

    def get_text(self):
        return self.channel.alternatives[0].transcript

class DeepgramConfig(BaseModel):
    detect_language: bool = False
    diarize: bool = False
    dictation: bool = False
    filler_words: bool = True
    language: str = "en-US"
    model: str = "nova-2-phonecall"
    punctuation: bool = False
    smart_format: bool = False
    utterances: bool = False
    encoding: str | None = "mulaw"
    sample_rate: int | None = 8000
    version: str = "latest"
    speech_final: bool = True
    endpointing: int | None = 10
    interim_results: bool | None = False


class Deepgram:

    def __init__(
        self,
        api_key: str,
        is_call_connected: asyncio.Event,
        conversation: CustomConversation,
        config: DeepgramConfig | None = None,
        on_output: OnOutput | None = None,
        on_input: OnInput | None = None,
        user_role: Role | None = None,
        debug: bool = False,
    ):
        """
        Instantiates the Deepgram service using the provided config.
        :param api_key:
        :type api_key:
        :param is_call_connected:
        :type is_call_connected:
        :param deepgram_config:
        :type deepgram_config:
        :param on_output:
        :type on_output:
        """

        self.input_queue: asyncio.Queue[str]|None = None
        self.output_queue: asyncio.Queue[str]|None = None
        self.websocket_connection = None
        self.api_key = api_key
        self.base_url = f"wss://api.deepgram.com/v1/listen"
        self.is_call_connected = is_call_connected
        self.config = config
        self.on_output = on_output
        self.on_input = on_input
        self.user_role: Role = user_role
        self.conversation: CustomConversation = conversation
        self.interrupter: Interrupter | None = None
        self.events: Events | None = None
        self.debug = debug
     

    async def on_output(self):
        pass

    async def connect(self):
        config = self.config or DeepgramConfig()
        config_options = config.model_dump()
        for key in list(config_options.keys()):
            if config_options[key] is None:
                del config_options[key]
        query_string = urlencode(config_options)
        logger.debug(f"query string: {query_string}")
        # converts the query string to lowercase because Deepgram doesn't recognize 'False' as a valid boolean
        url = self.base_url + f"?{query_string.lower()}"
        websocket_connection = await websockets.connect(
            url, extra_headers={"Authorization": f"Token {self.api_key}"}
        )
        self.websocket_connection = websocket_connection
        return websocket_connection

    async def send(self, ws: WebSocketClientProtocol, audio: bytes):
        if not ws:
            raise RuntimeError("Deepgram send does not have a websocket connection")
        await ws.send(audio)

    async def receive(self, ws: WebSocketClientProtocol):
        async for message in ws:
            transcription = json.loads(message)
            logger.debug(f"Deepgram received transcription: {transcription}")

    async def close(self):
        await self.websocket_connection.send(json.dumps({"type": "CloseStream"}))
        await self.websocket_connection.close()

    async def sender(
        self,
        ws: WebSocketClientProtocol,
        input_queue: asyncio.Queue,
        is_call_connected: asyncio.Event,
    ):
        # If the interrupter is not set, raise an error
        if not self.interrupter:
            raise ValueError("Interrupter not set")
        # Continue running while the call is still connected
        while is_call_connected.is_set():
            # pull next audio chunk from the input queue
            audio_chunk = await input_queue.get()
            if audio_chunk is None:
                await self.output_queue.put(None)
                await self.close()
                break
            # run the on_input method the user may supply
            # audio_chunk = self.on_input(audio_chunk)
            # preprocess the audio, so it is bytes
            # audio_chunk = bytes(audio_chunk)
            # Send audio chunk to Deepgram
            await self.send(ws, audio_chunk)

    async def receiver(
        self,
        ws: WebSocketClientProtocol,
    ):
        """
        Waits for transcription responses from Deepgram. This method is run as an asyncio task concurrently
        with the websocket sending. This makes sure receiving transcriptions is never blocked by awaiting the websocket
        send function
        :param ws:
        :type ws:
        """
        if not self.interrupter:
            raise ValueError("Interrupter not set")
        async for message in ws:
            response = json.loads(message)
            if response['type'] == "Metadata":
                logger.debug(
                    "Deepgram is breaking because it received metadata instead of a transcription"
                )
                break
            transcription= DeepgramTranscription(**response)
            transcription_text: str = transcription.channel.alternatives[0].transcript
            
            if transcription_text == "":
                continue
            # print('transcription: ', transcription_text)
            asyncio.create_task(
                    self.interrupter.check(int(transcription.duration * 1000))
                )
            if transcription.is_final and transcription_text != "":
                # when the final transcription is received we add it to the conversation
                content = transcription_text.strip()
                await self.conversation.add_message(role=self.user_role, content=content)
                # check_task = asyncio.create_task(self.interrupter.check())
                # await check_task
                # asyncio.create_task(
                #     self.interrupter.check(int(transcription["duration"] * 1000))
                # )
                await self.output_queue.put(transcription_text)


        
    async def start(
        self,
    ):
        print("deepgram starting")
        # Connect to the deepgram service through websockets
        websocket_connection = await self.connect()
        self.websocket_connection = websocket_connection
        await asyncio.gather(
            self.sender(websocket_connection, self.input_queue, self.is_call_connected),
            self.receiver(websocket_connection),
        )
        print("Deepgram start has completed")


# when we receive a transcription from Deepgram, pass it to the next FlowStep
# when the call disconnects, disconnect from Deepgram service, and destroy any queues Deepgram class created

class Transcriber(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def connect(self) -> WebSocketClientProtocol:
        pass

    @abstractmethod
    async def close(self):
        pass
        
    @abstractmethod
    async def add_audio(self, audio: bytes) -> typing.Any:
        pass

    @abstractmethod
    async def get_transcription(self) -> typing.Any:
        pass

    
class DeepgramTranscriber(Transcriber):
    def __init__(self, api_key: str, config: DeepgramConfig) -> None:
        super().__init__()
        self.api_key = api_key
        self.config = config
        self.websocket_connection: WebSocketClientProtocol | None = None
        self.base_url = f"wss://api.deepgram.com/v1/listen"
    
    async def connect(self) -> WebSocketClientProtocol:
        config_options = self.config.model_dump()
        for key in list(config_options.keys()):
            if config_options[key] is None:
                del config_options[key]
        query_string = urlencode(config_options)
        logger.debug(f"query string: {query_string}")
        # converts the query string to lowercase because Deepgram doesn't recognize 'False' as a valid boolean
        url = self.base_url + f"?{query_string.lower()}"
        websocket_connection = await websockets.connect(
            url, extra_headers={"Authorization": f"Token {self.api_key}"}
        )
        self.websocket_connection = websocket_connection
        return websocket_connection
    
    async def close(self):
        assert self.websocket_connection, "Deepgram websocket connection is not set"
        await self.websocket_connection.close()
    

    async def add_audio(self, audio: bytes):
        if not self.websocket_connection:
            raise RuntimeError("Deepgram send does not have a websocket connection")
        try:
            await self.websocket_connection.send(audio)
        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")
            return None
    
    async def get_transcription(self) -> DeepgramTranscription:
        assert self.websocket_connection, "Deepgram websocket connection is not set"

        message = await self.websocket_connection.recv()
        data = json.loads(message)
        transcription = DeepgramTranscription(**data)
        # logger.debug(f"Deepgram received transcription: {transcription}")
        return transcription