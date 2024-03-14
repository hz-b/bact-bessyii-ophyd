"""Libera box bpm: device interface

Warning:
   Currently in early stage of implementation
   Data on connection seem to always be available

"""
import numpy as np
from ophyd import Component as Cpt, Device, EpicsSignalRO, Kind, Signal
from ophyd.status import AndStatus, SubscriptionStatus
from enum import IntEnum


class ClockSyncState(IntEnum):
    """internal clocks, synchronised by hardware trigger?
    """
    nosync = 0
    tracking = 1
    synchronized = 2


class TriggerState(IntEnum):
    """

    Todo: is external the only sensible state?
    """
    external = 1

    
class CacheRead(Device):
    #: x channel to read from
    x_read = Cpt(EpicsSignalRO, ".X", kind=Kind.omitted)
    #: y channel to read from
    y_read = Cpt(EpicsSignalRO, ".Y", kind=Kind.omitted)
    #: x channel to use as storage
    x = Cpt(Signal, name=".x", value=[])
    #: y channel to use as storage
    y = Cpt(Signal, name=".y", value=[])

    def __init__(self, *args, timeout=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout=timeout

    def trigger(self):

        def cb_x(*, value, **kwargs):
            self.x.put(value)
            return True

        def cb_y(*, value, **kwargs):
            self.y.put(value)
            return True

        return AndStatus(
            SubscriptionStatus(self.x_read, cb_x, run=False, timeout=self.timeout),
            SubscriptionStatus(self.y_read, cb_y, run=False, timeout=self.timeout)
        )



class PointReadout(Device):
    """Read a single point from a single device
    """
    pt = Cpt(CacheRead, "signals:sa")
    # check that bpm is synchronised
    in_sync = Cpt(EpicsSignalRO, "clocks:sync_st_m")

    def stage(self):
        """

        todo: Should I check here that the libera box is synchronised?
        """
        if self.in_sync.get() != ClockSyncState.synchronized:
            raise AssertionError("Bpm not synchronized")

        return super().stage()

    def trigger(self):
        return self.pt.trigger()


class Triggers(Device):
    cnt = Cpt(EpicsSignalRO, "count_mon", name="cnt")
    src = Cpt(EpicsSignalRO, "source_mon", name="src")

    def stage(self):
        if self.src.get() != TriggerState.external:
            raise AssertionError("Trigger should be in external mode")

    
    
class TurnbyTurnDDCData(Device):
    """
    """
    tbt = Cpt(CacheRead, "signals:ddc_synth", name="tbt", timeout=12)
    trg = Cpt(Triggers, "triggers:t2:")
    
    def trigger(self):
        return self.tbt.trigger()

    
class TurnbyTurnTBTData(Device):
    """
    """
    tbt = Cpt(CacheRead, "signals:tdp_synth", name="tbt", timeout=12)
    trg = Cpt(Triggers, "triggers:t2:")

    def trigger(self):
        return self.tbt.trigger()
    

def test_libera_read_slow_data():
    from pprint import pprint

    slow_data = PointReadout("BPMZ5D8R:", name="sa")
    if not slow_data.connected:
        slow_data.wait_for_connection()

    slow_data.stage()
    status = slow_data.trigger()
    status.wait()
    status = slow_data.trigger()
    status.wait()

    print("slow data")
    pprint(slow_data.read())
    slow_data.unstage()


def test_libera_read_turn_by_turn():
    import datetime
    import pprint

    for cls in TurnbyTurnDDCData, TurnbyTurnTBTData:
        fast_data = TurnbyTurnDDCData("BPMZ5D8R:", name="tbt")
        if not fast_data.connected:
            fast_data.wait_for_connection(3)

        fast_data.stage()
        for i in range(3):
            start = datetime.datetime.now()
            print(f"{i}: wait for trigger")
            status = fast_data.trigger()
            flag = status.wait()
            end = datetime.datetime.now()
            print(f"{i}: wait for trigger {end-start},flagged {flag}")
            pprint.pprint(fast_data.read())
        fast_data.unstage()

        
def test_libera_read_fast_data():
    """need to understand why fast data behave so differently
    """
    from pprint import pprint

    
    fast_data = CacheRead("BPMZ5D8R:signals:fa", name="fa", timeout=20)
    if not fast_data.connected:
        fast_data.wait_for_connection(3)

    print(fast_data.x_read.get())
    print(fast_data.y_read.get())

    for i in range(3):
        print(f"fast data {i}: wait for trigger")
        status = fast_data.trigger()
        flag = status.wait()
        print(f"fast data {i}: trigger flagged {flag}")


if __name__ == '__main__':
    test_libera_read_slow_data()
    test_libera_read_fast_data()
    test_libera_read_turn_by_turn()
