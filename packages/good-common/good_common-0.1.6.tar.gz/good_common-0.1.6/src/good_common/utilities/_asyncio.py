import asyncio
import nest_asyncio
import sys
from typing import AsyncIterator, TypeVar, Callable, Awaitable
import signal

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


T = TypeVar("T")

def wrap_async_iterator(
    async_iter_func: Callable[..., AsyncIterator[T]]
) -> Callable[..., AsyncIterator[T]]:
    async def wrapper(*args, **kwargs) -> AsyncIterator[T]:
        stop_event = asyncio.Event()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, stop_event.set)
        
        try:
            async for item in async_iter_func(*args, **kwargs):
                if stop_event.is_set():
                    break
                yield item
                await asyncio.sleep(0)
        finally:
            loop.remove_signal_handler(signal.SIGINT)
    
    return wrapper