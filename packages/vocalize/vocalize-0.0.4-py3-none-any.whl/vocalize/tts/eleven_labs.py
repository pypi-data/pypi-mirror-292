import asyncio
import typing

import websockets
import json
from pydantic import BaseModel, ValidationError
import time

from vocalize.queues.queues import ElevenLabsOutputQueueDict
from ..flow.events import Events
from ..interrupter.interrupter import Interrupter, InterruptionError
from ..queues import ElevenLabsOutputQueue
from enum import Enum
from vocalize.log.propogate import logger


class ElevenVoices(Enum):
    Grace = "z9fAnlkpzviPz146aGWa"


class ElevenTimeoutError(Exception):
    pass


class NormalizedAlignment(BaseModel):
    charStartTimesMs: list[int]
    charDurationsMs: list[int]
    chars: list[str]


class ElevenResponse(BaseModel):
    audio: str | None
    isFinal: bool | None
    normalizedAlignment: NormalizedAlignment | None


class ElevenTimeout(BaseModel):
    message: str
    error: str
    code: int


# TODO: Need to implement error handling for when the quota is exceeded and alert the library user.
# TODO: Eleven Labs returns an error code of 1008 but it appears to return the same code for a connection timeout
# TODO: Possible solution idea: Use string parsing to determine error if Eleven Labs doesn't have meaningful errors
# TODO: Will need a way of identify if Eleven Labs has changed the the error string message that would break our parsing


class QuotaExceededError(Exception):
    def __init__(
        self,
        message: str = "Eleven Labs quota has been exceeded. Either upgrade your subscription or change providers.",
    ):
        self.message = message
        super().__init__(self.message)


class ElevenSendLimiter:
    """This is used to limit the rate at which the Eleven Labs TTS sends data to the websocket. If we don't have this, it will generate as fast as possible even if the user is going to interrupt before playback.

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        InterruptionError: _description_
        ElevenTimeoutError: _description_

    Returns:
        _type_: _description_
    """
    def __init__(self):
        self.is_ready_to_send = asyncio.Event()
        self.is_ready_to_send.set()
    
    async def wait_until_ready(self):
        await self.is_ready_to_send.wait() 

    def mark_ready(self):
        self.is_ready_to_send.set()
    
    def mark_not_ready(self):
        self.is_ready_to_send.clear()

class ElevenLabsConfig(BaseModel):
    voice_id: str | ElevenVoices
    model: typing.Literal[
        "eleven_monolingual_v1",
        "eleven_turbo_v2",
        "eleven_multilingual_v1",
        "eleven_multilingual_v2",
        "eleven_turbo_v2_5"
    ]
    stability: float = 0.5
    similarity_boost: float = 0.75
    optimize_streaming_latency: int = 3
    output_format: typing.Literal[
        "pcm_16000", "mp3_44100_128", "mp3_44100", "mp3_22050_32", "ulaw_8000"
    ] = "mp3_44100"
    style: int = 0
    use_speaker_boost: bool = True
    chunk_length_schedule: list[int] = [50, 150, 250, 350]


class ElevenLabs:
    def __init__(
        self,
        config: ElevenLabsConfig,
        is_call_connected: asyncio.Event,
        api_key: str,
        debug: bool,
        input_queue: asyncio.Queue | None = None,
        output_queue: asyncio.Queue | None = None,
        events: Events | None = None,
        interrupter: Interrupter | None = None,
        on_output: (
            typing.Callable[[ElevenLabsOutputQueueDict], typing.Awaitable[typing.Any]]
            | None
        ) = None,

        on_finished: typing.Callable[[], typing.Awaitable[None]] | None = None,
    ):
        self.debug = True
        self.config = config
        self.is_call_connected = is_call_connected
        self.input_queue: asyncio.Queue[str] | None = None
        self.output_queue: ElevenLabsOutputQueue | None = None
        self.base_url = "wss://api.elevenlabs.io/v1/text-to-speech/"
        self.on_output = on_output
        print(self.config.model_dump())
        self.voice_id = self.config.voice_id
        if isinstance(self.config.voice_id, ElevenVoices):
            self.voice_id = self.config.voice_id.value
        if not isinstance(self.voice_id, str):
            raise ValueError(
                f"ElevenLabs init was unable to set the voice_id to a string. Voice ID: {self.voice_id}"
            )
        self.url = f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input?model_id={self.config.model}&optimize_streaming_latency={self.config.optimize_streaming_latency}&output_format={self.config.output_format}"
        self.api_key = api_key
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.events = events
        self.interrupter = interrupter
        # this is changed when calling the self.stop() method
        self.is_allowed_to_continue = asyncio.Event()
        self.is_allowed_to_continue.set()

        self.send_limiter = ElevenSendLimiter()

        self.websocket: websockets.WebSocketClientProtocol | None = None
        self.bos_message = {
            "text": " ",
            "voice_settings": {
                "stability": self.config.stability,
                "similarity_boost": self.config.similarity_boost,
            },
            "generation_config": {
                "chunk_length_schedule": self.config.chunk_length_schedule
            },
            "xi_api_key": self.api_key,
        }
        self.eos_message = {"text": ""}
        self.times = []
        self.debug = debug
        self.is_not_generating: asyncio.Event = asyncio.Event()
        self.on_finished = on_finished

    async def send(
        self,
        websocket: websockets.WebSocketClientProtocol,
        text: str,
        try_trigger_generation: bool = True,
    ):
        # eleven labs expects the text to end with a space
        # if the text doesn't end with a space, add a space to the end of the text

        if self.debug:
            print(f"ElevenLabs.send() --- text length: {len(text)}")
        # TODO: This is a temporary fix. LLM is sometimes sending an empty string to the TTS.
        if text[-1] != " ":
            text += " "
        input_message = {
            "text": text,
            "try_trigger_generation": try_trigger_generation,
        }
        # print(
        #     f"ElevenLabs.send() --- awaiting websocket.send --- input_message: {input_message}"
        # )
        # print(
        #     f"ElevenLabs.send() --- json.dumps --- input_message: {json.dumps(input_message)}"
        # )
        # print(f"ElevenLabs.send() --- websocket: {websocket}")
        await self.websocket.send(json.dumps(input_message))

        # print(f"ElevenLabs.send() --- send task: {send_task}")
        # print(
        # f"ElevenLabs.send() --- after websocket.send() --- input_message: {input_message}"
        # )

    async def receive(
        self, websocket: websockets.WebSocketClientProtocol
    ) -> ElevenResponse | ElevenTimeout:
        try:
            response = await self.websocket.recv()
            data = json.loads(response)
            print("received response from eleven labs")
            # print('data: ', data)
            try:
                return ElevenResponse(**data)
            except ValidationError as e:
                print(f"validation error: {e.json} ")
                timeout_error = ElevenTimeout(**data)
                # if timeout_error.code == 1008:
                # raise QuotaExceededError()

                return timeout_error
        except websockets.exceptions.ConnectionClosedOK:
            print(
                "Eleven labs websocket was closed but just tried to receive. Returning empty dictionary"
            )
            await websocket.close()
            return ElevenResponse(audio=None, isFinal=True, normalizedAlignment=None)

    async def end(self, websocket: websockets.WebSocketClientProtocol):
        print(f"ElevenLabs.end() --- sending eos message")
        await self.websocket.send(json.dumps(self.eos_message))

    async def close(self, websocket: websockets.WebSocketClientProtocol):
        if self.debug:
            print(f"eleven labs closing websocket")
        assert self.websocket is not None, "Websocket is not set"
        await self.websocket.close()

    async def sender(self, websocket: websockets.WebSocketClientProtocol):
        logger.debug('starting eleven labs sender')
        if not self.interrupter:
            raise ValueError("Interrupter not set")

        self.send_limiter.mark_ready()
        while self.is_call_connected.is_set() and self.is_allowed_to_continue.is_set():
            # get text from the LLM, value will be None if the LLM has finished generating
            print("elevenlabs.sender() awaiting input_queue")
            async with self.interrupter.cancellable(
                self.send_limiter.wait_until_ready()
            ) as limiter_task:
                await limiter_task
                logger.critical('sent')
                self.send_limiter.mark_not_ready()

            async with self.interrupter.cancellable(
                self.input_queue.get()
            ) as text_task:
                print(f"cancellable with body --- text_task: {text_task}")
                text = await text_task

            print(f"eleven labs text: {text}")
            print(
                f"ElevenLabs.sender() --- self.is_not_generating.is_set(): {self.is_not_generating.is_set()}"
            )
            if text is None or len(text) == 0:
                # TODO: there is a chance the websocket will close before we receive the final audio response.
                await self.end(self.websocket)
                if self.debug:
                    print(f"eleven labs sent eos message")
                async with self.interrupter.cancellable(
                    self.is_not_generating.wait()
                ) as wait_task:
                    logger.debug('awaiting wait_task')
                    await wait_task
                logger.debug('awaiting self.close()')
                await self.close(self.websocket)
                logger.debug('eleven labs websocket closed, now breaking out of loop')

                break

            self.is_not_generating.clear()
            if self.debug:
                if len(self.times) == 0:
                    self.times.append(time.time())
            print("elevenlabs.sender() --- awaiting self.send()")
            await self.send(self.websocket, text)
            print("ElevenLabs.sender() --- after self.send()")
        if self.debug:
            print(f"Eleven Labs sender method reached end, now finished")

    async def receiver(self, websocket: websockets.WebSocketClientProtocol):
        assert self.output_queue is not None, "Output queue is not set"
        if not self.interrupter:
            raise ValueError("Interrupter not set")
        while self.is_call_connected.is_set() and self.is_allowed_to_continue.is_set():
            if self.events.is_interrupted.is_set():
                # need to set is_not_generating since the .sender() method waits for it before closing the websocket
                print(
                    f"ElevenLabs.receiver() detected interruption --- now raising InterruptionError"
                )
                raise InterruptionError()
            try:
                print("elevenlabs.receiver() --- awaiting self.receive()")
                async with self.interrupter.cancellable(
                    self.receive(websocket)
                ) as response_task:
                    response = await response_task

            except websockets.exceptions.ConnectionClosedError:
                print(
                    f"Eleven labs receiver was awaiting response but it's closed. breaking out of loop"
                )
                break
            except InterruptionError:
                print(
                    f"ElevenLabs.receiver() recieved an asyncio CancelledError. Continuing to next loop to catch interruption"
                )
                self.is_not_generating.set()
                continue
            if isinstance(response, ElevenTimeout):
                raise ElevenTimeoutError()
            assert isinstance(
                response, ElevenResponse
            ), "Response is not an instance of ElevenResponse"
            speech = response
            speech_dumped = speech.model_dump()
            if self.debug:
                print(
                    f"ElevenLabs.receiver() normalized alignment: {response.normalizedAlignment}"
                )
                time_taken = time.time() - self.times[0]
                print(f"Eleven labs first response time taken: {time_taken}")
            # print('speech: ', speech)
            text = ""
            if speech_dumped.get("normalizedAlignment"):
                text += "".join(speech_dumped["normalizedAlignment"]["chars"])
            if speech_dumped.get("isFinal"):
                await self.output_queue.put(None)
                self.is_not_generating.set()
                if self.on_finished is not None:
                    await self.on_finished()
                break

            print(
                f"elevenlabs.receiver() --- awaiting output_queue.put() ---- data snippet: {speech_dumped['audio'][:10]}"
            )

            await self.output_queue.put({"audio": speech_dumped["audio"], "text": text})
            self.send_limiter.mark_ready()
            if self.on_output is not None:
                await self.on_output({"audio": speech_dumped["audio"], "text": text})
        if self.debug:
            print(f"Eleven Labs receiver method reached end, now finished")

    async def start(self):
        if self.debug:
            print(f"Eleven labs start method")
        print("elvent labs url: ", self.url)
        self.interrupter.register(self.start)
        async for websocket in websockets.connect(self.url):
            logger.debug('eleven labs websocket loop first line')

            try:
                if self.debug:
                    logger.debug(f"Eleven labs websocket connected")
                await websocket.send(json.dumps(self.bos_message))
                print("sent bos message")
                self.websocket = websocket
                await asyncio.gather(self.receiver(websocket), self.sender(websocket))
            except ElevenTimeoutError:
                print(
                    f"Eleven labs websocket didn't receive text input, so it disconnected"
                )
                await websocket.close()
                continue
            except InterruptionError:
                print(
                    f"ElevenLabs.start() caught InterruptionError and is continuing to next connection loop"
                )
                await self.close(websocket)
                if self.events.is_interrupted.is_set():
                    print("ElevenLabs.start() waiting at start of connection iteration")
                    await self.interrupter.barrier.wait(self.start)
                continue
            finally:
                if self.debug:
                    print(
                        f"Eleven labs start, finally block is call set: {self.events.is_call_connected.is_set()}"
                    )
                if not self.events.is_call_connected.is_set():
                    logger.debug('eleven labs start is breaking out of loop since the call is not connected')
                    break
        print("Eleven labs start has completed")

    def stop(self):
        self.is_allowed_to_continue.clear()
