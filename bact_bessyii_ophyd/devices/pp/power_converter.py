import sys
import threading
import time

import numpy as np
from bact2.ophyd.devices.raw.multiplexer_state_machine import MuxerState
from bact2.ophyd.devices.raw.quad_list import quadrupoles
from bact2.ophyd.devices.utils import signal_with_validation, ReachedSetPoint
from bluesky.protocols import Movable
from ophyd import (Component as Cpt, Device, EpicsSignal, EpicsSignalRO, Kind, PVPositionerPC, Signal, )

from ophyd.device import DynamicDeviceComponent as DDC, Component
from ophyd.status import AndStatus, SubscriptionStatus, Status

from bact_mls_ophyd.devices.pp.selected_multiplexer import MultiplexerSelector

t_super = PVPositionerPC
t_super = ReachedSetPoint.ReachedSetpointEPS

_muxer_off = "Mux OFF"
_request_off = "Off"

_t_super = PVPositionerPC


class MultiplexerPowerConverter(t_super):
    readback = Cpt(EpicsSignal, ":rdbk")
    setpoint = Cpt(EpicsSignal, ":set")
    # switch = Cpt(EpicsSignal, ":cmd1")
    #: power converter on or off
    status = Cpt(EpicsSignalRO, ":stat1", kind=Kind.omitted)
    no_error = Cpt(EpicsSignalRO, ":stat2", kind=Kind.omitted)

    #: current that is small enough that switch off can be made
    tolerable_zero_current = Cpt(Signal, name="tolerable_error", value=20e-3, kind=Kind.config)

    #: acceptable relative error
    eps_rel = Cpt(Signal, name="eps_rel", value=6e-2, kind=Kind.config)

    #: execution stopped with a difference of 0.7 %
    #: at a value of 0.13
    eps_abs = Cpt(Signal, name="eps_abs", value=3e-2, kind=Kind.config)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("settle_time", 1.5)
        super().__init__(*args, **kwargs)

    def read(self):
        r = super().read()
        return r

    def set(self, value):
        txt = f"Setting power mux power converter to value {value}"
        self.log.debug(txt)

        stat2 = Status(settle_time=self.settle_time)

        def inform_finished(status):
            stat2.set_finished()

        stat1 = super().set(value)
        stat1.add_callback(inform_finished)

        stat = AndStatus(stat1, stat2)
        txt = (
                txt + f" status {stat} settle time {stat.settle_time} stat2 {stat2}" + " settle time {stat2.settle_time}")
        self.log.info(txt)
        return stat

    def _setToZero(self):
        try:
            self.setpoint.put(0.0, use_complete=False)
        except Exception as exc:
            self.log.error(f"Failed to put {self.setpoint} to 0.0")
            raise exc

    def setToZero(self):
        cls_name = self.__class__.__name__
        name = self.name
        try:
            self._setToZero()
        except Exception as exc:
            self.log.error(f"Failed to switch of {cls_name}(name={name}): reason({exc})")

    def isOff(self):
        value = self.readback.get()
        aval = np.absolute(value)
        eps_abs = self.eps_abs.get()
        flag = aval < eps_abs
        self.log.info(f"aval {aval} eps_abs {eps_abs}, flag {flag}")
        return flag

    def isOffText(self):
        pc_setp = self.setpoint.get()
        pc_rdbk = self.readback.get()
        pc_zc = self.tolerable_zero_current.get()
        txt = f"setpoint {pc_setp} readback {pc_rdbk} tolerable zero current {pc_zc}"
        return txt

    def stop(self, success=False):
        self.setToZero()

    def stage(self):

        val = self.status.get()
        if not val:
            self.log.warning(f"Muxer power converter off! val = {val} still trying")

        val = self.no_error.get()
        if not val:
            self.log.warning(f"Muxer power converter signals error val = {val}, still trying")

        super().stage()

    def unstage(self):
        self.setToZero()
        super().unstage()
