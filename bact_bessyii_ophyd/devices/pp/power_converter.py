import asyncio
from typing import List, Union, Any

import numpy as np
from bluesky.protocols import Movable, Stageable, Stoppable, Status
from ophyd_async.core import (
    StandardReadable,
    HintedSignal,
    AsyncStatus,
    observe_value,
    WatchableAsyncStatus,
)
from ophyd_async.core.utils import WatcherUpdate
from ophyd_async.epics.signal import epics_signal_r, epics_signal_rw


# from ophyd.status import AndStatus, Status


class ResettingPowerConverter(StandardReadable, Stageable, Movable, Stoppable):
    """
    Todo:
        move to bact core ophyd or to bact custom bessyii_mls
    """

    def __init__(
        self,
        prefix: str,
        *,
        name="",
        readback_suffix: str = "rdbk",
        setpoint_suffix: str = "set",
        ref_val_suffix: str = None,
        atol: float,
        rtol: float,
        timeout: float
    ):

        assert atol > 0
        assert rtol > 0
        assert timeout > 0

        with self.add_children_as_readables(HintedSignal):
            self.readback = epics_signal_r(float, prefix + readback_suffix)

        self.precision = epics_signal_r(int, prefix + readback_suffix + ".PREC")
        self.units = epics_signal_r(str, prefix + readback_suffix + ".EGU")
        self.setpoint = epics_signal_rw(float, prefix + setpoint_suffix)
        self.atol = float(atol)
        self.rtol = float(rtol)
        self.timeout = float(timeout)

        self.reference_value = None
        self.reference_value_signal = None
        if ref_val_suffix is not None:
            self.reference_value_signal = epics_signal_rw(
                float, prefix + ref_val_suffix
            )

        super().__init__(name=name)

    def set_name(self, name: str):
        """
        Todo:
            Need to find out if setting name is convienience or necessity
        """
        super().set_name(name)
        # Readback should be named the same as its parent in read()
        self.readback.set_name(name)

    async def stage(self) -> Union[Status, List[Any]]:
        if self.reference_value_signal is not None:
            self.reference_value = await self.reference_value_signal.get_value()
        return super().stage()

    @WatchableAsyncStatus.wrap
    async def set(self, new_position: float, timeout: float = None) -> Status:
        """
        see :class:`ophyd_async.epics.demo.Mover` for comparison
        """
        timeout = timeout or self.timeout
        self._set_success = True
        old_position = await self.setpoint.get_value()

        # Make an Event that will be set on completion, and a Status that will
        # error if not done in time
        done = asyncio.Event()
        done_status = AsyncStatus(asyncio.wait_for(done.wait(), timeout))
        # Wait for the value to set, but don't wait for put completion callback

        old_position, units, precision, = await asyncio.gather(
            self.setpoint.get_value(),
            self.units.get_value(),
            self.precision.get_value(),
        )

        await self.setpoint.set(new_position, wait=False)
        async for current_position in observe_value(
            self.readback, done_status=done_status
        ):
            yield WatcherUpdate(
                current=current_position,
                initial=old_position,
                target=new_position,
                name=self.name,
                unit=units,
                precision=precision,
            )
            if np.isclose(
                current_position, new_position, rtol=self.rtol, atol=self.atol
            ):
                done.set()
                break
        if not self._set_success:
            raise RuntimeError("Motor was stopped")

    async def stop(self, success=True):
        self._set_success = success
        print("Stopping setting back to %s" % (self.reference_value,))
        if self.reference_value is not None:
            status = await self.set(self.reference_value)
            return status
