from bact_bessyii_mls_ophyd.devices.utils.power_converters_as_multiplexer import (
    ScaledPowerConverter,
    SelectedPowerConverter,
    MultiplexerSetMixin,
)
from ophyd import Component as Cpt, Device, Kind, Signal
from ophyd.areadetector.base import ad_group
from ophyd.device import DynamicDeviceComponent as DDC

from . import  steerer_list

t_steerers = [(name.lower(), name) for name in steerer_list.horizontal_steerers[:3]   + steerer_list.vertical_steerers[:3]
              #
              ]
steerer_names = [elem[0] for elem in t_steerers]


class SteererCollection(Device, MultiplexerSetMixin):
    """

    Todo:
        Belongs to the multiplexer
    """

    power_converters = DDC(
        ad_group(ScaledPowerConverter, t_steerers, kind=Kind.normal, lazy=False),
        doc="all steerers",
        default_read_attrs=(),
    )

    power_converter_names = Cpt(
        Signal, name="steerer_names", value=steerer_names, kind=Kind.config
    )

    sel = Cpt(SelectedPowerConverter, name="sel_pc")

    _default_config_attrs = ("steerer_names",)
    _default_read_attrs = ("sel",)

    def get_element_names(self):
        return self.power_converter_names.get()

if __name__ == "__main__":
    sc = SteererCollection("Pierre:DT:", name="sc")
    if not sc.connected:
        sc.wait_for_connection()

    print(sc.read())
