"""
"""
# from ophyd import Component as Cpt, Device, EpicsSignalRO, Kind, Signal
# from ophyd.status import SubscriptionStatus
from ophyd_async.core import StandardReadable, AsyncStatus
from ophyd_async.epics.signal.signal import epics_signal_rw
from numpy.typing import NDArray
import pytest

from ..utils.sync import wait_for_new_data


class BPM(StandardReadable):
    def __init__(self, prefix: str, name=""):
        with self.add_children_as_readables():
            self.count = epics_signal_rw(float, prefix + ":count")
            # Twin has to export the same data as machine so int16
            self.bdata = epics_signal_rw(NDArray[float], prefix + ":bdata")
            #self.bdata = epics_signal_rw(NDArray[np.int16], prefix + ":bdata")

        super().__init__(name=name)

    async def read(self):
        await wait_for_new_data(self.bdata)
        return super().read()


@pytest.mark.skip
async def test_bpm():
    """pytest compatible
    """
    prefix = "Pierre:DT:"
    # prefix = ""
    cntr = BPM(prefix + "MDIZ2T5G", name="bpm")

    await cntr.connect(timeout=1)
    data = await cntr.read()
    print('1: ', data[cntr.name + '-count']['value'])
    data = await cntr.read()
    print('2: ', data[cntr.name + '-count']['value'])

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
