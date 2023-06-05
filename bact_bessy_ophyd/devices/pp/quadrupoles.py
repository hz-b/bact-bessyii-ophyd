from bact_bessyii_mls_ophyd.devices.utils.power_converters_as_multiplexer import (
    ScaledPowerConverter,
    SelectedPowerConverter,
    MultiplexerSetMixin,
)

from ophyd.areadetector.base import ad_group
from ophyd import Component as Cpt, Device, Kind, Signal
from ophyd.device import DynamicDeviceComponent as DDC


quad_prefixes_q1 = [
    # First short
    "Q1P1K1RP",
    "Q1P2K1RP",
    # second: long
    "Q1P1L2RP",
    "Q1P2L2RP",
    # Third short
    "Q1P1K3RP",
    "Q1P2K3RP",
    # Forth long
    "Q1P1L4RP",
    "Q1P2L4RP",
]

quad_prefixes_q2 = [name.replace("Q1", "Q2") for name in quad_prefixes_q1]
quad_prefixes_q3 = [name.replace("Q1", "Q3") for name in quad_prefixes_q1]
quad_prefixes = quad_prefixes_q1 + quad_prefixes_q2 + quad_prefixes_q3

t_quads = [(name.lower(), name) for name in quad_prefixes]
quad_names = [elem[0] for elem in t_quads]


class QuadrupolesCollection(Device, MultiplexerSetMixin):
    """

    Todo:
        Belongs to the multiplexer
    """

    power_converters = DDC(
        ad_group(ScaledPowerConverter, t_quads, kind=Kind.normal, lazy=False),
        doc="all quadrupoless ",
        default_read_attrs=(),
    )

    power_converter_names = Cpt(
        Signal, name="quad_names", value=quad_names, kind=Kind.config
    )

    sel = Cpt(SelectedPowerConverter, name="sel_pc")

    _default_config_attrs = ("quad_names",)
    _default_read_attrs = ("sel",)


if __name__ == "__main__":
    qc = QuadrupolesCollection(name="qc")
    if not qc.connected:
        qc.wait_for_connection()

    print(qc.read())
