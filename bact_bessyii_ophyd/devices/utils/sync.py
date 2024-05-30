import asyncio
from asyncio import Event
from typing import Union

async def wait_for_new_data(signal, timeout: Union[float|None]= None, event: Event = None):
    """
    Todo:
        should one leave it to the user to clear the event?

        s there a simpler fashion to do this?
    """
    if event is None:
        event = Event()

    cnt = 0
    def cb(value):
        ""
        nonlocal cnt
        if cnt > 0:
            event.set()
        cnt += 1

    signal.subscribe_value(cb)
    # Todo: can this operation fail?
    if timeout is None:
        await event.wait()
    else:
        await asyncio.wait_for(event.wait(), timeout=timeout)
    signal.clear_sub(cb)
