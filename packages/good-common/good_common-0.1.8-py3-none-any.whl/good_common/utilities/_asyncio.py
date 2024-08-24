import asyncio
import nest_asyncio
import sys
from typing import AsyncIterator, TypeVar, Callable, Awaitable, overload
import signal
import functools
from loguru import logger

def run_async(coroutine):
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no current event loop, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Check if we're in a Jupyter notebook
    if "IPython" in sys.modules:
        # If so, apply nest_asyncio to allow nested use of event loops
        nest_asyncio.apply()

    # Now we can safely run our coroutine
    return loop.run_until_complete(coroutine)


async def _async_generator_timeout(async_gen, timeout):
    try:
        while True:
            try:
                item = await asyncio.wait_for(async_gen.__anext__(), timeout)
                yield item
            except StopAsyncIteration:
                break
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError("Generator didn't emit a new item within the specified timeout")



T = TypeVar("T")

@overload
def async_iterator(
    func: Callable[..., AsyncIterator[T]]
) -> Callable[..., AsyncIterator[T]]: ...

@overload
def async_iterator(
    func: None = None,
    iteration_timeout: float | None = None
) -> Callable[[Callable[..., AsyncIterator[T]]], Callable[..., AsyncIterator[T]]]: ...


def async_iterator(
    func: Callable[..., AsyncIterator[T]] | None = None,
    iteration_timeout: float | None = None,
) -> Callable[..., AsyncIterator[T]] | Callable[[Callable[..., AsyncIterator[T]]], Callable[..., AsyncIterator[T]]]:
   
    def inner(async_iter_func: Callable[..., AsyncIterator[T]]) -> Callable[..., AsyncIterator[T]]:
        @functools.wraps(async_iter_func)
        async def wrapper(*args, **kwargs) -> AsyncIterator[T]:
            stop_event = asyncio.Event()

            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, stop_event.set)
            
            try:
                
                if iteration_timeout is not None:
                    async_gen = _async_generator_timeout(async_iter_func(*args, **kwargs), iteration_timeout)
                else:
                    async_gen = async_iter_func(*args, **kwargs)
                
                async for item in async_gen:
                    if stop_event.is_set():
                        break
                    yield item
                    await asyncio.sleep(0)
            except* Exception as e:
                for exc in e.exceptions:
                    logger.error(exc)
            finally:
                loop.remove_signal_handler(signal.SIGINT)
        return wrapper
    
    if func is not None:
        return inner(func)
    
    return inner
    