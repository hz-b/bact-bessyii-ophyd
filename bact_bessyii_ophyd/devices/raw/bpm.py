"""BESSY II Bpm blocked data
"""
from ophyd_async.core import StandardReadable
from ophyd_async.epics.signal.signal import epics_signal_rw
from numpy.typing import NDArray
from numpy.core import int16

from ..utils.sync import new_data_available


class BPM(StandardReadable):
    def __init__(self, prefix: str, name="", timeout: float = 3.0):
        self.timeout = timeout
        with self.add_children_as_readables():
            self.count = epics_signal_rw(float, prefix + ":count")
            # Twin has to export the same data as machine: so int16
            self.bdata = epics_signal_rw(NDArray[int16], prefix + ":bdata")

        super().__init__(name=name)

    async def new_data_available(self):
        await new_data_available(self.bdata, timeout=self.timeout)

    async def read(self):
        return await super().read()
