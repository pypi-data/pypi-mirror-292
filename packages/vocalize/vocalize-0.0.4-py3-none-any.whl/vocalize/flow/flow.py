import asyncio
from starlette.websockets import WebSocket


from .flowstep import FlowStep
import typing
from ..interrupter.interrupter import Interrupter
from .events import Events, IsCallConnected
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vocalize.phone import Call, TwilioCall
    from asyncio import Event
    from vocalize.conversation.role import Roles
    from vocalize.stt.deepgram import Deepgram
    from vocalize.tts.eleven_labs import ElevenLabs
    from vocalize.llm.llm import LocalLLM

class FlowQueue(typing.TypedDict):
    """
    Holds the audio queue that connects two FlowSteps together as well as identifies the steps that use the queue.
    """

    input: FlowStep | None
    output: FlowStep | None
    queue: asyncio.Queue[typing.Any]


class Flow:
    def __init__(
        self,
        input: "TwilioCall | None",
        stt: "Deepgram | None" ,
        llm: "LocalLLM",
        tts: "ElevenLabs",
        roles: "Roles",
        output: "TwilioCall | None",
        debug: bool | None = None,
        benchmarking: bool = False,
        tts_output_queue_max_size: int = 0,
        llm_tts_queue_max_size: int = 0,
    ):
        """
        Used to control the flow of data through the flow steps

        :param input: The flow step that acts as the input to the flow. It will generate/define data that is passed along.
        :type input: Any class that has a .send method
        :param stt:
        :type stt:
        :param llm:
        :type llm:
        :param tts:
        :type tts:
        :param output: The step that handles outputting the data. Can be the same as input. Typically: phone call or device audio
        :type output:
        :param user_role: The role that represents the user. It is used when a transcription is created.
        :type user_role: Role
        :param assistant_role: The role that represents the AI. It is used when the output processes the generated audio.
        :type assistant_role: Role
        :param debug: Enables debug mode, which adds profiling, time logging, and print statements.
        :type debug: bool
        """
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.output = output
        self.input = input
        flow_steps = [input, stt, llm, tts]
        if output is not input:
            flow_steps.append(output)
        self.flow_steps = [step for step in flow_steps if step is not None]
        self.benchmarking = benchmarking
        # tts_output queue maxsize is used to prevent over generation of TTS audio samples.
        # TTS will await the queue.put() causing it to block sending new text to TTS until the previous outputs have been handled
        self.tts_output_queue: asyncio.Queue[bytes] = asyncio.Queue(
            maxsize=tts_output_queue_max_size
        )  # the pure audio bytes without base64 encoding.
        self.llm_tts_queue: asyncio.Queue[str] = asyncio.Queue(
            maxsize=llm_tts_queue_max_size
        )
        # stt -> llm queue is only being used to indicate a new transcription is ready. The actual data is pulled from the Conversation.
        self.stt_llm_queue: asyncio.Queue[str] = asyncio.Queue()
        self.input_stt_queue: asyncio.Queue[str] = asyncio.Queue()
        if self.output:
            self.output.role = roles.assistant
        self.debug = debug
        self.queues: typing.List[asyncio.Queue[typing.Any]] | list[FlowQueue] = [
            self.tts_output_queue,
            self.llm_tts_queue,
            self.stt_llm_queue,
            self.input_stt_queue,
        ]
        self.is_interrupted: Event = asyncio.Event()
        self.is_call_connected = IsCallConnected()
        self.is_call_connected.set()
        # Storing the asyncio.Events in a Pydantic model because it cleans up the number of arguments a
        # flow step needs to accept in the __init__ and stores the events in one place.
        is_turn_complete = asyncio.Event()
        is_turn_complete.set()
        self.events = Events(
            is_call_connected=self.is_call_connected,
            is_interrupted=self.is_interrupted,
            is_turn_complete=is_turn_complete,
        )
        self.interrupter = Interrupter(
            queues=[
                self.tts_output_queue,
                self.llm_tts_queue,
            ],
            events=self.events,
            debug=self.debug if self.debug is not None else False,
        )
        self.initialize_steps()
        self.create_queues()
        
        self.tasks: list[asyncio.Task[typing.Any]] = []

    def initialize_steps(self) -> None:
        """
        Adds the interrupter, and events to each step in the flow. By default, all events will receive
        these items
        :return: None
        :rtype: None
        """
        for step in self.flow_steps:
            step.events = self.events
            step.interrupter = self.interrupter

    def assign_queues(self):
        if self.input is self.output:
            self.input.input_queue = self.tts_output_queue
        else:
            self.output.input_queue = self.tts_output_queue
        self.input.output_queue = self.input_stt_queue
        self.stt.input_queue = self.input_stt_queue
        self.stt.output_queue = self.stt_llm_queue
        self.llm.input_queue = self.stt_llm_queue
        self.llm.output_queue = self.llm_tts_queue
        self.tts.input_queue = self.llm_tts_queue
        self.tts.output_queue = self.tts_output_queue

    def create_queues(
        self,
    ) -> None:
        steps = self.flow_steps
        queues: list[FlowQueue] = [{"queue": asyncio.Queue[typing.Any](), "input": None, "output": None} for _ in range(len(steps))]
        for step_idx, step in enumerate(steps):
            step.output_queue = queues[step_idx]["queue"]
            step.input_queue = queues[step_idx - 1]["queue"]
            queues[step_idx]["input"] = step
            queues[step_idx - 1]["output"] = step
        print("queues: ", queues)
        self.queues = queues

    async def start(self):
        for step in self.flow_steps:
            if self.debug is not None:
                step.debug = self.debug
            self.tasks.append(asyncio.create_task(step.start()))
        self.tasks.append(asyncio.create_task(self.interrupter.start()))

        await asyncio.gather(*self.tasks)

        print("end of Flow.start()")

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        
