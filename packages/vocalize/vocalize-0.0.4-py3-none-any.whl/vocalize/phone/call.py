import asyncio
import base64
import typing
from abc import ABCMeta, abstractmethod

from vocalize.conversation.role import Role

from loguru import logger
from ..conversation import Conversation
from ..conversation.conversation import CustomConversation
from ..flow.events import Events
from ..interrupter.interrupter import Interrupter, InterruptionError
from starlette.websockets import WebSocket, WebSocketDisconnect
from ..queues import ElevenLabsOutputQueue
import time


class Call(metaclass=ABCMeta):
    def __init__(self, sid: str | int, websocket: WebSocket, config=None): ...

    def preprocess(self): ...

    @abstractmethod
    def receive(self): ...

    @abstractmethod
    def send(self, audio: bytes) -> None: ...

    def postprocess(self): ...

    def __iter__(self):
        return self

    def __next__(self):
        return bytes("Hello World!", "utf-8")


OnOutput = typing.Callable[[bytes], typing.Awaitable]


class CallQueue(typing.TypedDict):
    text: str
    audio: bytes


class TwilioCall:
    def __init__(
        self,
        websocket: WebSocket,
        conversation: CustomConversation,
        sid: str | int | None = None,
        on_output: OnOutput | None = None,
        config=None,
        debug: bool = False,
    ):
        self.sid = sid
        self.websocket = websocket
        self.config = config or None
        self.input_queue: ElevenLabsOutputQueue = asyncio.Queue()
        self.output_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.is_call_connected: asyncio.Event | None = None
        self.config = config if config else None
        self.conversation: CustomConversation = conversation
        self.role: Role | None = None
        self.interrupter: Interrupter | None = None
        self.events: Events | None = None
        self.debug = debug

    async def receive(self) -> bytes | None:
        data = await self.websocket.receive_json()
        if data["event"] == "start":
            logger.debug(f"TwilioCall.receive() --- data: {data}")
            self.stream_sid= data["start"]["streamSid"]
            self.sid = data["start"]["callSid"]
        if data["event"] == "media":
            audio = data["media"]["payload"]
            # decode the base64 byte string received from Twilio
            decoded_audio = base64.b64decode(audio)
            return decoded_audio
        else:
            return None

    async def send(self, audio: str) -> None:
        # Take the audio bytes and convert it to base64 bytes
        # base64_encoded_audio = base64.b64encode(audio)
        # Convert the audio bytes into a string representation
        # base64_string = base64_encoded_audio.decode('utf-8')
        # Create the json payload that Twilio expects
        message = {
            "event": "media",
            "streamSid": str(self.stream_sid),
            "media": {"payload": audio},
        }
        await self.websocket.send_json(message)

    async def send_in_chunks(
        self,
        audio: str,
        milliseconds_of_audio_per_chunk: int,
        milliseconds_to_sleep_between_chunks: int,
    ) -> None:

        print(f"Length of audio: {len(audio)}")

        if (
            milliseconds_to_sleep_between_chunks
            > milliseconds_of_audio_per_chunk
        ):
            raise ValueError(
                "Should never sleep longer than the audio duration of the chunk. Doing so, will cause "
                "the audio to be choppy between chunks. The current audio duration in milliseconds of the"
                f" audio chunk is: milliseconds_of_audio_per_chunk={milliseconds_of_audio_per_chunk}. "
                f"The current duration of the sleep in milliseconds is: "
                f"milliseconds_to_sleep_between_chunks={milliseconds_to_sleep_between_chunks}. "
                f"If you're unsure a good default would be sleep for 30 milliseconds less than the audio duration. "
                f"In this case, set milliseconds_to_sleep_between_chunks={milliseconds_of_audio_per_chunk - 10}"
            )

        # TODO: Handle the instance where a user passes in a chunk size that is actually bigger than the audio received.
        # TODO: If the user is basing their sleep duration based off chunk size, it will cause stuttery playback
        # TODO: Add this as a warning to the user.
        # in order to calculate the number of characters per millisecond
        # 1. Take the number of characters per byte
        # chars_per_byte = 3 / 4  # base64 encoding has 4 characters to represent 3 bytes

        # 2. Calculate the number of bytes per millisecond
        # num_bytes = (len(audio) * chars_per_byte)
        # print(f"number bytes in audio: {num_bytes}. Time: {num_bytes / 8000} ")
        # the audio is mulaw encoded, using 1 byte per sample and 8000 samples per second. 8,000 bytes per second
        # bytes_per_second = 8000
        # bytes_per_millisecond = bytes_per_second / 1000  # 8 bytes per millisecond

        # 3. Multiply the characters/byte and bytes/millisecond
        # The units are characters/byte & bytes/millisecond. The bytes cancel out and left with characters/millisecond
        # num_chars_per_millisecond = chars_per_byte * bytes_per_millisecond

        # this number is a static value, so I precomputed in my head. Example code is commented above.
        number_base64_characters_per_millisecond = 8
        chunk_size = (
            number_base64_characters_per_millisecond
            * milliseconds_of_audio_per_chunk
        )
        time_last_sent = time.perf_counter()
        for i in range(0, len(audio), chunk_size):
            # if self.debug:
            #     print(f"looping in send_in_chunk")
            if self.events.is_interrupted.is_set():
                # print('call.send_in_chunks() waiting at barrier')
                await self.interrupter.barrier.wait(self.send_in_chunks)
                print(
                    f"send_in_chunks is breaking because of interruption event"
                )
                break
            # print(
            #     f"it took {time.perf_counter() t} seconds to reach the send audio function again"
            # )
            await self.send(audio[i : i + chunk_size])
            # print(
            #     f"it took {time.perf_counter() - time_last_sent} seconds to send the audio again"
            # )
            time_last_sent = time.perf_counter()
            seconds_to_sleep = milliseconds_to_sleep_between_chunks / 1000
            await asyncio.sleep(seconds_to_sleep)
            # if self.debug:
            #     print(
            #         f"call send in chunks woke up after {time.perf_counter() - time_last_sent} seconds "
            #         f"when it was scheduled to sleep for {seconds_to_sleep} seconds"
            #     )

    async def sender(self):
        if not self.interrupter:
            raise ValueError("Interrupter not set")
        self.interrupter.register(self.sender)
        websocket = self.websocket
        while self.events.is_call_connected.is_set():
            if self.events.is_interrupted.is_set():
                await self.interrupter.barrier.wait(self.sender)
            try:
                async with self.interrupter.cancellable(self.input_queue.get()) as data_task:
                    data = await data_task
            except InterruptionError:
                continue

               
            # if self.debug:
                # print(f"TwilioCall.sender() --- data: {data}")
            # when a new input is received, set the output to running
            if data is not None:
                # base64 encoding stores 3 bytes of data in 4 characters. So "ABCD" would be 3 bytes.
                if "audio" in data and data["audio"]:
                    try:
                        send_in_chunks_coro = self.send_in_chunks(data['audio'], 200, 150)
                        async with self.interrupter.cancellable(send_in_chunks_coro) as send_in_chunks_task:
                            await send_in_chunks_task
                    except InterruptionError:
                        continue
                   
                print("sender finished sending audio in chunks")

                text = data["text"]
                print("text to add to conversation: ", text)
                await self.conversation.add_message(self.role, text)
            else:
                # None is used as an "I'm finished" message so set the output to Not running
                self.events.is_turn_complete.set()
                print(
                    f"TwilioCall.sender() --- set is_turn_complete. events.is_turn_complete.is_set(): {self.events.is_turn_complete.is_set()}"
                )
        self.interrupter.deregister(self.sender)

    async def receiver(self):
        if not self.interrupter:
            raise ValueError("Interrupter not set")
        while self.events.is_call_connected.is_set():
            audio = await self.receive()
            if audio is not None:
                await self.output_queue.put(audio)

    async def start(self):
        try:
            await asyncio.gather(self.receiver(), self.sender())
        except WebSocketDisconnect as error:
            print("websocket disconnected, call ended")
            self.events.is_call_connected.clear()

        await self.output_queue.put(None)
        print("TwilioCall has finished")
