from ophyd import (
    Component as Cpt,
    Device,
    FormattedComponent as FC,
    Kind,
    EpicsSignalRO,
    Signal,
)
from ophyd.status import AndStatus, SubscriptionStatus


class TuneChannel(Device):
    freq = FC(EpicsSignalRO, "{self.prefix}:rd{self.plane}")
    timeout = Cpt(Signal, name="timeout", value=3, kind=Kind.config)

    def __init__(self, prefix, *, plane: str = None, **kwargs):
        assert plane is not None
        self.plane = plane
        super().__init__(prefix, **kwargs)

    def trigger(self):
        def cb(**kwargs):
            return True

        stat = SubscriptionStatus(self.freq, cb, run=False, timeout=self.timeout.get())
        return stat


class Tunes(Device):
    """

    Todo:
       Learn handling prefixes for TuneChannel properly!
    """
    x = Cpt(TuneChannel, "", name="x", plane="H")
    y = Cpt(TuneChannel, "", name="y", plane="V")
    # z = Cpt(TuneChannel, "", name="z", plane="Z")

    #def trigger(self):
    #    return AndStatus(
    #        AndStatus(self.x.trigger(), self.y.trigger()), self.z.trigger()
    #    )


if __name__ == "__main__":
    tn = Tunes("TUNEZRP", name="tn")
    if not tn.connected:
        tn.wait_for_connection()

    stat = tn.trigger()
    stat.wait(10)
    print(tn.read())
    print(tn.y.freq.describe())
