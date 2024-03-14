import numpy as np
from ophyd import Component as Cpt, Device, EpicsSignalRO, Kind
from ophyd.status import AndStatus, SubscriptionStatus


class CacheRead(Device):
    x_read = Cpt(EpicsSignalRO, ".X", value=[], kind=Kind.omitted)
    #: y channel to read from
    y_read = Cpt(EpicsSignalRO, ".Y", value=[], kind=Kind.omitted)
    #: x channel to use as storage
    x = Cpt(EpicsSignalRO, ".xs", value=[])
    #: y channel to use as storage
    y = Cpt(EpicsSignalRO, ".ys", value=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def trigger(self):
        def cb_x(*, value, **kwargs):
            self.x.put(value)
        def cb_y(*, value, **kwargs):
            self.y.put(value)

        return AndStatus(
            SubscriptionStatus(self.x_read, cb_x, 0.1),
            SubscriptionStatus(self.y_read, cb_y, 0.1)
        )


class PointReadout(Device):
    """
    """
    x = Cpt(EpicsSignalRO, ".X", value=np.nan)
    y = Cpt(EpicsSignalRO, ".Y", value=np.nan)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def stage(self):
        """Should I check here that the libera box is synchronised?
        """
        return super().stage()

    def unstage(self):
        """
        just here fore
        """
        return super().unstage()

    def trigger(self):
        def cb(**kwargs):
            return True

        return AndStatus(
            SubscriptionStatus(self.x, cb, 0.1),
            SubscriptionStatus(self.y, cb, 0.1)
        )


class WaveformReadout(Device):
    """

    Instrument is currently issuing data in a constant fashion.
    This device will take the data recieved and stored locally
    afther trigger was sent

    Warning:
        current setup requires to buffer data locally
        next trigger could arrive before data is read out
    """
    #:
    x_read = Cpt(EpicsSignalRO, ".X", value=[], kind=Kind.omitted)
    #: y channel to read from
    y_read = Cpt(EpicsSignalRO, ".Y", value=[], kind=Kind.omitted)
    #: x channel to use as storage
    x = Cpt(EpicsSignalRO, ".xs", value=[])
    #: y channel to use as storage
    y = Cpt(EpicsSignalRO, ".ys", value=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def trigger(self):
        def cb_x(*, value, **kwargs):
            self.x.put(value)
        def cb_y(*, value, **kwargs):
            self.y.put(value)

        return AndStatus(
            SubscriptionStatus(self.x_read, cb_x, 0.1),
            SubscriptionStatus(self.y_read, cb_y, 0.1)
        )




class LiberaBPM(Device):
    slow = Cpt(PointReadout, ":signal.sa")
    fast = Cpt(WaveformReadout, ":signal.sa")
    # check in control room what it should be
    # fast = Cpt(ContinousUpdate, ":signal.sa")


