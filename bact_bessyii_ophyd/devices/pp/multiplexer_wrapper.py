from typing import Sequence

from ophyd import (
    Device,
    EpicsSignal,
    PVPositionerPC
)
from ophyd.device import DynamicDeviceComponent as DDC

from bact_bessyii_ophyd.devices.pp.quadrupoles import quadrupole_names
from bact_bessyii_mls_ophyd.devices.utils import reached_setpoint
t_super = PVPositionerPC
t_super = reached_setpoint.ReachedSetpointEPS

_muxer_off = "Mux OFF"
_request_off = "Off"

_t_super = PVPositionerPC


class MultiplexerPCWrapper(Device):
    pcs = DDC(
        {
            name: (EpicsSignal, ":" + name, dict(put_complete=True))
            for name in quadrupole_names
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
