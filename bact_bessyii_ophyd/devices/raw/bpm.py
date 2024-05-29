"""
"""
# from ophyd import Component as Cpt, Device, EpicsSignalRO, Kind, Signal
# from ophyd.status import SubscriptionStatus
from ophyd_async.core import StandardReadable, ConfigSignal, HintedSignal, wait_for_connection
from ophyd_async.epics.signal.signal import epics_signal_r, epics_signal_rw, epics_signal_x
from typing import Sequence
from numpy.typing import NDArray
import numpy as np


class BPM(StandardReadable):
    def __init__(self, prefix: str, name=""):
        with self.add_children_as_readables():
            self.count = epics_signal_rw(float, prefix + ":count")
            self.bdata = epics_signal_rw(NDArray[np.int16], prefix + ":bdata")

        super().__init__(name=name)

    # def trigger(self):
    #    def cb(**kwargs):
    #        """new data here"""
    #        return True
    #
    #    timeout = self.timeout.get()
    #    return SubscriptionStatus(self.packed_data, cb, run=False, timeout=timeout)


async def test_bpm():
    """pytest compatible
    """
    prefix = "Pierre:DT:"
    prefix = ""
    bpm = BPM(prefix + "MDIZ2T5G", name="bpm")

    # if not bpm.connected:
    #    bpm.wait_for_connection()

    await bpm.connect(timeout=1)

    print(bpm.name)
    data = await bpm.read()

async def test_bpm_aioca():
    from aioca import caget, connect

    cnt_name = 'MDIZ2T5G:count'
    bdata_name = 'MDIZ2T5G:bdata'

    await connect(cnt_name, bdata_name)
    tsk_cnt = caget('MDIZ2T5G:count')
    tsk_bdata  = caget('MDIZ2T5G:bdata')
    cnt = await tsk_cnt
    bdata = await tsk_bdata
    print(cnt)
    print(bdata)


if __name__ == "__main__":
    import asyncio
    # asyncio.run(test_bpm_aioca())
    asyncio.run(test_bpm())
