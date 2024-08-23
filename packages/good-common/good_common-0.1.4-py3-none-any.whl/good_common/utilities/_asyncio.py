import asyncio
import nest_asyncio
import sys


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
