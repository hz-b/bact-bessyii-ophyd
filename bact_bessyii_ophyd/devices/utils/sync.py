from asyncio import Event, wait_for
from typing import Union


async def wait_for_new_data(signal, timeout: Union[float | None] = None, event: Event = None):
    """waits that new data arrive at the signal

    If taking longer than timeout, an asyncio.TimeoutError will
    be raised.

    Warning:
        if you pass an event, is your responsibility to clear it
        before you call this function.

        If unsure, do not supply an event

    """
    event = event or Event()

    cnt = 0
    def cb(value):
        "count that data has been set a second time"
        nonlocal cnt
        if cnt > 0:
            event.set()
        cnt += 1

    signal.subscribe_value(cb)
    try:
        await wait_for(event.wait(), timeout=timeout)
    finally:
        # also unsubscribe in case of timeouts
        signal.clear_sub(cb)
