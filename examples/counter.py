from ophyd_async.core import StandardReadable
from ophyd_async.epics.signal import epics_signal_rw

from bact_bessyii_ophyd.devices.utils.sync import new_data_available

class Counter(StandardReadable):
    def __init__(self, prefix: str, name="", timeout: float=1.0):
        self.timeout = timeout
        with self.add_children_as_readables():
            self.counter = epics_signal_rw(float, prefix + ":counter")
        super().__init__(name=name)

    async def new_data_available(self) -> None:
        await new_data_available(self.counter, timeout=self.timeout)

    async def read(self):
        return await super().read()


async def test_counter():
    prefix = "Pierre:DT:"
    # prefix = ""
    cntr = Counter(prefix + "dt", name="counter")
    await cntr.connect(timeout=1)

    await cntr.new_data_available()
    r = await cntr.read()
    print(r[cntr.counter.name]['value'])
    await cntr.new_data_available()
    r = await cntr.read()
    print(r[cntr.counter.name]['value'])


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_counter())
