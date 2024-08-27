import websockets
import copy
from abc import ABCMeta, abstractmethod
from ..conversation import Conversation
from ..conversation.conversation import CustomConversation
from ..flow import FlowStep
from .config import LLMConfig
import typing
import httpx
import asyncio
from ..interrupter.interrupter import Interrupter, InterruptionError
from ..flow.events import Events
import time


class MaxLengthError(Exception):
    def __init__(
        self,
        message: str = "Your LLM instance has reached the maxmimum available token length and is returning empty strings. Either reduce conversation length or implement recursive summarization.",
    ):
        super().__init__(message)


class LLM(metaclass=ABCMeta):
    def __init__(self): ...

    def parse(self):
        """
        Different LLM providers have different formats for how they return the LLM completion.
        This method is responsible for parsing the completion response and returning it as a string
        :return:
        :rtype:
        """
        ...

    def serialize(self):
        """
        Take the string that represents the conversation history and convert it back into a
        format that the LLM provider will understand
        :return:
        :rtype:
        """
        ...

    def preprocess(self): ...

    def postprocess(self): ...

    @abstractmethod
    def send(self, conversation: typing.Any):
        """
        Take the properly formatted conversation history and send it to the LLM provider.
        :param conversation:
        :type conversation:
        :return: None
        :rtype: None
        """
        ...

    @abstractmethod
    def receive(self): ...

    def __iter__(self): ...

    def __next__(self): ...


class LocalLLM(FlowStep):
    def __init__(
        self,
        protocol: str,
        host: str,
        port: int | None,
        is_call_connected: asyncio.Event,
        conversation: CustomConversation,
        slug: str | None,
        debug: bool,
        config: LLMConfig | None = None,
        on_finished: typing.Callable[[str], typing.Awaitable[None]] | None = None,
    ):
        self.debug = debug
        self.protocol = protocol
        self.host = host
        self.port = port
        self.slug = slug
        if self.port is None:
            self.url = f"{self.protocol}://{self.host}/llm"
        else:
            self.url = f"{self.protocol}://{self.host}:{self.port}/llm"
        self.config = config or self.create_config()
        self.conversation: CustomConversation = conversation
        self.ws = None
        self.input_queue: asyncio.Queue | None = None
        self.output_queue: asyncio.Queue | None = None
        self.is_call_connected = is_call_connected
        self.interrupter: Interrupter | None = None
        self.events: Events | None = None
        print(f"LLM generation max tokens: {self.config.generation_max_tokens}")
        self.client: httpx.AsyncClient | None = None
        self.on_finished = on_finished

    def create_config(self):
        config = LLMConfig(
            turn_max_tokens=100,
            generation_max_tokens=20 if self.debug else 20,
            stopping_tokens=["<_(-"],
        )
        return config

    async def connect(self):
        full_url = f"ws://{self.host}:{self.port}"
        async with websockets.connect(full_url) as ws:
            self.ws = ws

    async def send(self, prompt: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json={
                    "prompt": prompt,
                    "num_new_tokens": self.config.generation_max_tokens,
                },
            )
            return response.json()

    async def receive(self, completion: str):
        return completion

    async def start(self):
        print(f"LLM debug: {self.debug}")
        if self.events is None:
            raise ValueError("Events is not set in LocalLLM")
        if not isinstance(self.interrupter, Interrupter):
            raise TypeError(f"LocalLLM's interrupter is {self.interrupter}. Make sure the LocalLLM instance has an Interrupter instance at self.interrupter")
        self.interrupter.register(self.start)
        self.client = httpx.AsyncClient()
        while self.is_call_connected.is_set():
            if self.events.is_interrupted.is_set():
                await self.interrupter.barrier.wait()
            try:
                async with self.interrupter.cancellable(
                    self.input_queue.get()
                ) as prompt_task:
                    prompt = await prompt_task

            except InterruptionError:
                print(
                    f"LocalLLM.start() input_queue.get() task raised CancelledError --- Waiting at barrier"
                )
                await self.interrupter.barrier.wait(self.start)
                continue

            if prompt is None:
                await self.output_queue.put(None)
                break
            async with self.interrupter.cancellable(
                self.loop_until_finished(
                    stopping_tokens=self.config.stopping_tokens,
                    max_length=self.config.turn_max_tokens,
                )
            ) as completion_task:
                completion = await completion_task
            # completion = await self.loop_until_finished(
            #     stopping_tokens=self.config.stopping_tokens,
            #     max_length=self.config.turn_max_tokens,
            # )
            if self.debug:
                print(f"LLM start has finished loop")
            # completion = await self.receive(completion)
            # print('llm outputting completion to queue after loop finished. Completion: ', completion)
            # await self.output_queue.put(completion)
        print("LocalLLM start has finished")
        self.interrupter.deregister(self.start)
        await self.client.aclose()

    async def get_completion(self, prompt: str):
        """
        Handles sending the prompt and returning the completion using the class instance's httpx client.
        :param prompt: Prompt to send to the LLM service
        :type prompt: str
        :return:
        :rtype:
        """
        if not self.client:
            raise RuntimeError("LocalLLM does not have a httpx client initialized.")
        response = await self.client.post(
            self.url,
            json={
                "prompt": prompt,
                "num_new_tokens": self.config.generation_max_tokens,
            },
        )
        if self.debug:
            print("LocalLLM.get_completion() --- llm response: ", response.json())
        return response.json()

    def find_first_stopping_token_index(
        self,
        stopping_tokens: list[str],
        completion: str,
    ):
        # check if completion contains one of the stopping tokens and mark the starting index of
        # the first stopping token. There could be more than one stopping token in a completion
        first_stopping_token_index = None
        for token in stopping_tokens:
            if token in completion:
                if first_stopping_token_index is None:
                    first_stopping_token_index = completion.index(token)
                else:
                    # if the current token starts before the earliest seen so far, go with the current token
                    if completion.index(token) < first_stopping_token_index:
                        first_stopping_token_index = completion.index(token)
        return first_stopping_token_index

    def crop_completion_if_spaces(self, completion: str):
        """Crop completion
        
        Test Cases: 
        1. "Hello my name is" -> "Hello my name"
        2. "Hey" -> "Hey"
        3. " Hey" -> " Hey"
        4. " Hello my name is" -> " Hello my name"
        5. "   " -> "   "
        6. "  Hey how " -> "  Hey"

        Args:
            completion (str): _description_
        """
        completion_copy = copy.copy(completion)
        completion_split = completion_copy.split(" ")
        real_word_count = 0
        for word in completion_split:
            if real_word_count >= 2:
                break
            if word != "":
                real_word_count += 1

        if real_word_count >= 2:
            completion_copy_cleaned = completion_copy.rstrip()
            completion_copy_cleaned_split = completion_copy_cleaned.split(" ")
            completion_copy_final = " ".join(completion_copy_cleaned_split[:-1])
            return completion_copy_final

        if real_word_count == 1:
            return completion_copy.rstrip()
        if real_word_count == 0:
            return completion_copy
        else:
            raise ValueError(
                f"Unexpected real_word_count: {real_word_count} for completion: {completion}"
            )

    async def single_loop(
        self,
        running_completion: str,
        stopping_tokens: list[str],
    ):
        print("LLM looping")
        if not self.is_call_connected.is_set():
            return None
        # take conversation and add the running completion to the end of it.
        prompt = f"{self.conversation.assistant_prompt}{running_completion}"
        # if self.debug:
        # print("llm loop_until_finished prompt: ", prompt)
        # get completion
        start_time = time.perf_counter()
        completion: str = await self.get_completion(prompt)
        print('llm completion: ', completion)

        # remove any trailing whitespace on the very end of the completion since we sometimes get trailing whitespace. 
        # I'm not sure why this happens, but if we don't remove it, the last character of the completion will be considered a space so the function to remove everything before the last word won't work properly.
        # completion = completion.rstrip()

        # Since we are sending each completion chunk to the output queue, we need to check if it ends with a
        # stopping token. We don't want the TTS to generate audio for a cropped stopping token. For example:
        # STOPPING TOKEN: "USER:"
        # COMPLETION: "How are you doing today? US"
        # COMPLETION: "ER: I am doing well, thank you."
        # Since the completion ends with "US", it could avoid detection as a stopping token and get passed to TTS

        #  We need to crop the last word of the completion in case it is a cropped version of a stopping token.
        # index_of_last_space = completion.rfind(" ")
        # if index_of_last_space != -1:
        #     completion = completion[:index_of_last_space]

        first_stopping_token_index = self.find_first_stopping_token_index(
            stopping_tokens=stopping_tokens, completion=completion
        )
        # If the completion has a stopping token, crop the completion, send to output queue, and end loop
        if first_stopping_token_index is not None or completion == "":
            completion = completion[:first_stopping_token_index]
            print('llm completion after stopping token cropping: ', completion)
            print(
                "LocalLLM.single_loop() --- awaiting output_queue.put() with completion"
            )
            await self.output_queue.put(completion)
            print(
                "LocalLLM.single_loop() --- awaiting output_queue.put() with None, which represents a completed state"
            )
            await self.output_queue.put(None)
            is_finished = True
            if self.debug:
                print(f"llm finished by reaching a stopping token:")
            return None

        # if there is not a stopping token in the completion, the remove the last word in case of a cropped stopping token
        completion = self.crop_completion_if_spaces(completion)
        print('llm completion after word cropping: ', completion, )

        if completion == "":
            raise MaxLengthError()



        # If the length of the new completion + running completion is longer than max length, handle cropping and
        # end the loop
        if len(running_completion) + len(completion) >= self.config.turn_max_tokens * 4:
            num_characters_left_before_max = (self.config.turn_max_tokens * 4) - len(
                running_completion
            )
            completion = completion[:num_characters_left_before_max]
            print('llm completion after max length cropping: ', completion)
            print(
                "LocalLLM.single_loop() --- awaiting output_queue.put() with completion"
            )
            await self.output_queue.put(completion)
            is_finished = True

            print(
                "LocalLLM.single_loop() --- awaiting output_queue.put() with None, which represents a completed state"
            )
            await self.output_queue.put(None)
            if self.debug:
                print(
                    f"llm loop finished due to max length. Max length: {self.config.turn_max_tokens}. "
                    f"Running length with new completion: {len(running_completion) + len(completion)}"
                    f"Cropped completion: {completion}"
                )
            return None

        if self.debug:
            print(f"llm sending completion to queue. Completion: {completion}")
        await self.output_queue.put(completion)
        print(f"llm single loop took {time.perf_counter() - start_time}")
        return completion

    async def loop_until_finished(
        self,
        stopping_tokens: typing.List[str],
        max_length: int,
    ):
        """
        Continue generating LLM completions until either the output includes a stopping token or the output
        reaches the maximum allowed length.
        """
        self.events.is_turn_complete.clear()
        print("set llm is running ")
        is_finished = False
        running_completion = ""
        while not is_finished:
            if self.events.is_interrupted.is_set():
                print("LocalLLM waiting at barrier")
                await self.interrupter.barrier.wait(self.loop_until_finished)
                print("LocalLLM finished waiting at barrier")
                break

            completion_coro = self.single_loop(
                running_completion,
                stopping_tokens,
            )
            try:
                async with self.interrupter.cancellable(
                    completion_coro
                ) as completion_task:
                    completion = await completion_task
            except InterruptionError:
                continue

            if completion is None:
                if self.on_finished:
                    await self.on_finished(running_completion)
                break
            running_completion += completion

        return running_completion

    async def __aiter__(self):
        return self

    async def __anext__(self): ...

    def __iter__(self):
        return self

    def __next__(self): ...
