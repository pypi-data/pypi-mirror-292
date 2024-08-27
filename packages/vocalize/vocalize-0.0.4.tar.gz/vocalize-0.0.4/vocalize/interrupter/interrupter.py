import time
import asyncio
import typing
import sys
import types
import inspect
from typing import TYPE_CHECKING
# import interrupter.cancellable.Cancellable
from loguru import logger

from vocalize import interrupter as interrupter_module

logger.add(sys.stderr, enqueue=True)

if TYPE_CHECKING:
    from flow import Flow
    from flow.events import Events


class InterruptionError(Exception):
    def __init__(self, message: str = 'The user has interrupted the generation. This error is intended to be caught and used as needed.'):
        super().__init__(message)

class InterrupterBarrier(asyncio.Barrier):
    def __init__(
        self,
        parties: int,
        events: "Events",
        callback: typing.Callable[[], typing.Any] | None = None,
    ):
        super().__init__(parties)
        self.waiting_parties = []
        self.events = events
        self.callback = callback

    async def wait(
        self,
        func: typing.Callable[[typing.Any], typing.Any] | None = None,
    ) -> int:
        # logger.info(
        #     f"InterrupterBarrier.wait() called by {func} --- Total parties needed: {self.parties} --- Current number waiting: {self.n_waiting}"
        # )
        self.waiting_parties.append(func)
        # logger.info(
            # f"InterrupterBarrier.wait() --- currently waiting parties: {self.waiting_parties}"
        # )
        result = await super().wait()
        # logger.info(
            # f"InterrupterBarrier successfully passed super().wait() call --- returning"
        # )
        # logger.success('Interruption has been successfully handled and all FlowSteps have finished waiting at InterrupterBarrier')
        self.waiting_parties = []
        # logger.info(f"Function {func} is exiting barrier")
        # asyncio Barrier frees the tasks in reverse order of when they started waiting. So the most recent task to call .wait() is the first one freed
        if result == 0:
            if self.callback:
                self.callback()
        return result


class Cancellable:
    def __init__(self, interrupter: "Interrupter"):
        self.interrupter = interrupter

    def __call__(self, func: types.CoroutineType, *args: typing.Any, **kwargs: typing.Any):
        print(f"__call__ func: {func}")
        if not inspect.iscoroutine(func):
            raise TypeError(
                f"Cancellable function received MUST be a coroutine --- function received: {func} --- Make sure you have 'called' the coroutine and given it the required arguments. Ex: my_coro('first arg', 'second arg') "
            )
        self.task = asyncio.create_task(func)
        print(f"task: {self.task}")
        return self

    def enter_handler(self):
        self.interrupter.register_cancellable(self.task)
        return self.task

    def exit_handler(self, exc_type, exc_value, exc_tb):
        print(f"exc_type: {exc_type} -- exc_value: {exc_value} -- exc_tb: {exc_tb}")
        self.interrupter.deregister_cancellable(self.task)
        # information regarding determining the correct type
        # https://stackoverflow.com/questions/58808055/what-are-the-python-builtin-exit-argument-types
        if exc_type is asyncio.CancelledError:
            raise InterruptionError()

    def __enter__(self):
        print('Cancellable.__enter__')
        return self.enter_handler()

    def __exit__(self, exc_type, exc_value, exc_tb):
        print('Cancellable.__exit__')
        self.exit_handler(exc_type, exc_value, exc_tb)

    async def __aenter__(self):
        print('Cancellable.__aenter__')
        return self.enter_handler()

    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        print('Cancellable.__aexit__')
        self.exit_handler(exception_type, exception_value, exception_traceback)


class Interrupter:
    def __init__(
        self,
        queues: list[asyncio.Queue[typing.Any]],
        events: "Events",
        debug: bool = True,
        on_interrupt: typing.Callable[[], typing.Any] | None = None,
    ):
        self.queues = queues
        self.interruptables: set[typing.Callable[[typing.Any], typing.Any]] = set()
        self.cancellables: set[typing.Callable[[typing.Any], typing.Any]] = set()
        self.num_interruptables = 0
        self.events: Events = events
        self.barrier = self.create_barrier()
        self.debug: bool = True
        self.sensitivity: str = 'relaxed'
        self.duration_threshold: int = 500
        self.on_interrupt = on_interrupt

    def cancellable(self, func):
        # cancellable is a context manager
        # Need to return a new Cancellable instance each time since one instance represents one task
        # When I tried to reuse the same instances, sometimes a task would try to be removed twice. Causing an error
        cancellable = Cancellable(self)
        return cancellable(func)

    def register_cancellable(self, func):
        # logger.info(f"Interrupter registering cancellable: {func}")
        self.cancellables.add(func)

    def deregister_cancellable(self, func):
        # logger.info(f"Interrupter deregistering cancellable: {func}")
        self.cancellables.remove(func)

    def register(self, func):
        self.interruptables.add(func)
        # logger.info(f"registering func: {func}. new total: ", len(self.interruptables))
        self.barrier = self.create_barrier()

    def deregister(self, func) -> None:
        self.interruptables.remove(func)
        print(f"Interrupter deregistered function: {func} ---- Creating new barrier")
        self.barrier = self.create_barrier()

    def create_barrier(self):
        return InterrupterBarrier(
            len(self.interruptables) or 1, self.events, self.barrier_callback
        )

    def flush_queues(self):
        for queue in self.queues:
            self.flush_queue(queue)
        if self.debug:
            logger.success(f"Finished flushing queues. Flushed queues: {self.queues}")
        # await self.barrier.wait()
        self.events.is_interrupted.clear()

    def flush_queue(self, queue: asyncio.Queue[typing.Any]):
        while True:
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    def cancel_all(self):
        for item in self.cancellables:
            item.cancel()
        # self.cancellables = set()
        logger.success(
            f"Interrupter canceled all cancellable tasks --- Total cancelled: {len(self.cancellables)}"
        )

    def barrier_callback(self):
        self.events.is_interrupted.clear()
        self.events.is_turn_complete.set()
        self.flush_queues()

    async def check(self, duration_in_milliseconds: int):
        if not isinstance(duration_in_milliseconds, int):
            raise TypeError("Interrupter.check() received a duration_in_milliseconds that is NOT an integer. Make sure duration_in_milliseconds is an 'int'")
        logger.debug(f"is_turn_complete: {self.events.is_turn_complete.is_set()}")
        if not self.events.is_turn_complete.is_set() and duration_in_milliseconds > self.duration_threshold:
            logger.info("interrupted check has determined there is an interruption")
            self.events.is_interrupted.set()
            logger.debug(
                f"Barrier parties: {self.barrier.parties} ---- Interruptables: {self.interruptables}"
            )
            logger.debug(f"Barrier number already waiting: {self.barrier.n_waiting}")
            self.cancel_all()
            logger.debug(
                f"Barrier number already waiting after cancelling tasks: {self.barrier.n_waiting}"
            )
            if self.on_interrupt:
                self.on_interrupt()
            await self.barrier.wait(self.check)
            logger.debug(
                f"Interrupter.check() --- self.events.is_interrupted.is_set(): {self.events.is_interrupted.is_set()}"
            )
            logger.debug(
                f"Interrupter.check() --- self.events.is_turn_complete.is_set(): {self.events.is_turn_complete.is_set()}"
            )
            # self.interruptables = set()

    async def start(self):
        self.register(self.start)


def interruptable(func):
    async def wrapper(*args, **kwargs):
        await func(*args, **kwargs)

    return wrapper
