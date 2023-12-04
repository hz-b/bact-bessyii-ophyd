"""
"""
from ophyd import Component as Cpt, Device, EpicsSignalRO, EpicsSignal, Kind, Signal
from ophyd.status import SubscriptionStatus, AndStatus
from threading import Event

class BPMPlane(Device):
    """One plane (x, or y)"""
    pos = Cpt(EpicsSignalRO, ":pos")
    rms = Cpt(EpicsSignalRO, ":rms")

    def trigger(self):
        """ensure all data are new

        emitted from a single ioc: waiting to use p4p
        """
        def cb(**kwargs):
            """new data here"""
            return True

        timeout = self.parent.timeout.get()

        return AndStatus(
            SubscriptionStatus(self.pos, cb, run=False, timeout=timeout),
            SubscriptionStatus(self.rms, cb, run=False, timeout=timeout)
        )


class BPMIntensity(Device):
    z = Cpt(EpicsSignalRO, ":z")
    s = Cpt(EpicsSignalRO, ":s")


class BPMRawData(Device):
    """some data that seems to be direct from internals ..."""
    stat = Cpt(EpicsSignalRO, ":stat")
    gain = Cpt(EpicsSignalRO, ":gain")


class BPMConfig(Device):
    """

    Todo:
        make all signals readonly
    """
    names = Cpt(EpicsSignal, ":names", kind=Kind.config)
    s = Cpt(EpicsSignal, ":s", kind=Kind.config)


class BPM(Device):
    x = Cpt(BPMPlane, ":x")
    y = Cpt(BPMPlane, ":y")
    intensity = Cpt(BPMIntensity, ":intensity")
    raw = Cpt(BPMRawData, ":raw")
    cfg = Cpt(BPMConfig, ":par")
    count = Cpt(EpicsSignalRO, ":im:count")
    timeout = Cpt(Signal, name="timeout", value=3, kind=Kind.config)

    def trigger(self):
        return AndStatus(self.x.trigger(), self.y.trigger())


def test_bpm():
    """pytest compatible
    """
    prefix = "Pierre:DT:"
    bpm = BPM(prefix + "bpm", name="bpm")
    if not bpm.connected:
        bpm.wait_for_connection()

    print(bpm.read_configuration())
    return
    stat = bpm.trigger()
    stat.wait(3)
    data = bpm.read()
    print(data)
    bpm_data = data["bpm_x_rms"]["value"]
    print(bpm_data)
    bpm_names = data["bpm_names"]["value"]
    print(bpm_names)


if __name__ == "__main__":
    test_bpm()
