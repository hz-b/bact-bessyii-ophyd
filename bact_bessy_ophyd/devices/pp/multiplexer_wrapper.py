import sys
import threading
import time
from typing import Sequence

import numpy as np
from bact2.ophyd.devices.raw.multiplexer_state_machine import MuxerState
from bact2.ophyd.devices.raw.quad_list import quadrupoles
from bact2.ophyd.devices.utils import signal_with_validation, ReachedSetPoint
from bluesky.protocols import Movable
from ophyd import (
    Component as Cpt,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    Kind,
    PVPositionerPC,
    Signal,
)

from ophyd.device import DynamicDeviceComponent as DDC, Component
from ophyd.status import AndStatus, SubscriptionStatus, Status

from bact_mls_ophyd.devices.pp.power_converter import MultiplexerPowerConverter
from bact_mls_ophyd.devices.pp.selected_multiplexer import MultiplexerSelector

t_super = PVPositionerPC
t_super = ReachedSetPoint.ReachedSetpointEPS

_muxer_off = "Mux OFF"
_request_off = "Off"

_t_super = PVPositionerPC


class MultiplexerPCWrapper(Device):
    pcs = DDC(
        {
            name: (EpicsSignal, ":" + name, dict(put_complete=True))
            for name in quadrupoles
        },
        doc="the multiplexer power converter selector pvs",
        default_read_attrs=(),
    )

    def get_element_names(self) -> Sequence[str]:
        """
        Returns:
            the names of the elements the multiplexer can connect to
        """
        return self.pcs.component_names
