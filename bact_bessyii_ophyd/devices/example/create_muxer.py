import sys

# import matplotlib
#
# matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from bluesky.simulators import check_limits
from cycler import cycler
from bluesky.protocols import Movable
from functools import partial
import sys
import bluesky.plans as bp
from databroker import catalog

from bact_mls_ophyd.devices.pp import bpm
from bact_mls_ophyd.devices.pp.multiplexer import Multiplexer, MultiplexerPCWrapper, MultiplexerSelector, \
    MultiplexerPowerConverter


def main():
    prefix = sys.argv[1]
    bpm_devs = bpm.BPM(prefix + "MDIZ2T5G", name="bpm")
    # BESSY 2
    bpm_devs.configure(dict(n_valid_bpms=128))

    muxer = Multiplexer(prefix, name="mux")
    # and empty compound multiplexer
    # create an empty slected multiplexer
    # create an empty power converter
    # create an empty wrapper
    #  assign a  selected multiplexer
    #  assign a  power converter
    #  assign a  wrapper

    # muxer.set_selected_multiplexer("PMUXZR", name="sel")
    if not muxer.connected:
        muxer.wait_for_connection(timeout=5)
    assert isinstance(muxer.selected_multiplexer, Movable)
    print(muxer.describe())

    lt = LiveTable(
        [
            muxer.selected_multiplexer.selected.name,
            muxer.power_converter.setpoint.name,
            muxer.power_converter.readback.name,
            "qc_sel_p_setpoint",
            "qc_sel_r_setpoint",
            "qc_sel_p_readback",
            "qc_sel_r_readback",
            bpm_devs.count.name,
            # cs.name,
            # tn.x.freq.name,
            # tn.y.freq.name,
        ],
        default_prec=10
    )

    power_converter_names = muxer.get_power_converter_names()
    cyc_magnets = cycler(muxer.selected_multiplexer, power_converter_names)
    currents = np.array([0, -1, 0, 1, 0]) * 5e-1
    cyc_currents = cycler(muxer.power_converter, currents)
    # cyc_count = cycler(cs, range(3))
    cmd = partial(bp.scan_nd, [bpm_devs], cyc_magnets * cyc_currents)

    md = dict(machine="BESSYII", nickname="bba", measurement_target="beam_based_alignment",
              target="digital twin development",
              comment="understanding interaction between twin and bluesky"
              )
    RE = RunEngine(md)
    # def receive_document(name, doc):
    #     """Access to the data for debugging
    #
    #     """
    #     pass
    # RE.subscribe(receive_document)
    db = catalog["heavy"]

    # RE.subscribe(db.v1.insert)
    uids = RE(cmd(), [lt])
    print(f"Measurement uid {uids}")


if __name__ == "__main__":
    plt.ion()
    try:
        main()
    except:
        raise
    else:
        pass
        plt.ioff()
        plt.show()
