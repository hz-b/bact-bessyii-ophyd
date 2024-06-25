from typing import Sequence, Union, List, Any

from bluesky.protocols import Stageable, Movable, Stoppable, Status
from ophyd_async.core import StandardReadable, DeviceVector

from .power_converter import ResettingPowerConverter


class PowerconverterCollection(StandardReadable, Stageable, Movable, Stoppable):
    def __init__(self,
        prefix: str,
        *,
        name="",
        power_converters: Sequence[ResettingPowerConverter]
    ):
        self._power_converters = power_converters
        self._selected_powerconverter_name = self._power_converters[0].get_name()
        super().__init__(name=name)
        DeviceVector

    async def stage(self) -> Union[Status, List[Any]]:
        """
        Todo:
            stage all of them and
        """
        return await super().stage()

    async def unstage(self) -> Union[Status, List[Any]]:
        """
        Todo:
            stage all of them and
        """
        return await super().unstage()

    async def set(self, name: str) -> Status:
        """
        """
        assert name in [pc.name for pc in self._powerconverters]
        self._selected_powerconverter_name = name

    async def read(self, value) -> Status:
        """
        """



