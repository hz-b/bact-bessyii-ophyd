from typing import Sequence

import ophyd.status
from bact2.ophyd.devices.utils import signal_with_validation, ReachedSetPoint
from ophyd import (
    Component as Cpt,
    Device,
    PVPositionerPC
)

from .multiplexer_wrapper import MultiplexerPCWrapper
from .power_converter import MultiplexerPowerConverter
from .selected_multiplexer import MultiplexerSelector

_muxer_off = "Mux OFF"
_request_off = "Off"


# multiplexerCompound
class Multiplexer(Device):
    """
    This is a multipexer compound which includes:
        a selected multiplexer
        a power converter
        and a list of power converter's names (activate)
    """
    # list of member attributes:
    selected_multiplexer = Cpt(MultiplexerSelector, "PMUXZR", name="selected_multiplexer")
    power_converter = Cpt(
        MultiplexerPowerConverter,
        "QSPAZR",
        name="power_converter",
        egu="A",
        setting_parameters=0.05 * 2,
        settle_time=2,
        timeout=20,
    )
    wrapper = Cpt(MultiplexerPCWrapper, "PMUXZR", name="wrapper")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_wrapper(self):
        return self.wrapper

    def get_power_converter(self):
        return self.power_converter

    def get_selected_multiplexer(self):
        return self.selected_multiplexer

    #  member functions
    def stage(self):
        return super().stage()

    def unstage(self):
        self.power_converter.unstage()
        self.selected_multiplexer.unstage()
        return super().unstage()

    def describe(self):
        data = super().describe()
        return data

    def get_element_names(self) -> Sequence[str]:
        return self.wrapper.get_element_names()
