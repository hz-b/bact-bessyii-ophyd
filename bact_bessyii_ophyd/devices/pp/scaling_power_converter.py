"""
Todo:
    check how to use pseudo devices with ophyd async
"""
from abc import ABCMeta, abstractmethod

from ophyd_async.core import StandardReadable, WatchableAsyncStatus
from bluesky.protocols import Movable, Stageable, Stoppable, Status, Reading


class MapCoordinateSystem(metaclass=ABCMeta):
    @abstractmethod
    def forward(self, value: object) -> object:
        pass

    @abstractmethod
    def inverse(self, value: object) -> object:
        pass


class LinearMapCoordinateSystem(MapCoordinateSystem):
    def __init__(self, offset: float, scale: float):
        self.offset = offset
        self.scale = scale

    def forward(self, value: float) -> float:
        return value * self.scale + self.offset

    def reverse(self, value: float) -> float:
        return (value - self.offset) / self.scale


class ScalingDevice(StandardReadable, Stageable, Movable, Stoppable):
    def __init__(self, prefix, *, name="", actuator, mapping_device):
        self.actuator = actuator
        self.mapping_device = mapping_device
        super().__init__(name)

    @WatchableAsyncStatus.wrap
    async def set(self, value) -> Status:
        return self.actuator.set(self.mapping_device.forward(value))

    async def read(self) -> dict[str, Reading]:
        tmp = await self.actuator.read()
        #: Todo map data back
        r = tmp.copy()
        # replace setpoint and readback
        r.setpoint
        return r