from bact_bessyii_mls_ophyd.devices.utils.power_converters_as_multiplexer import MultiplexerSetMixin, \
    ScaledPowerConverter, SelectedPowerConverter
from .steerer_configuration_repository import ConfigurationRepository
from ophyd import Component as Cpt, Device, DynamicDeviceComponent as DDC, Kind, Signal
from ophyd.areadetector import ad_group

repo = ConfigurationRepository()


class SteererCollection(Device, MultiplexerSetMixin):
    """Steerers with scaling to value
    """

    power_converters = DDC(
        ad_group(ScaledPowerConverter, [(name, name) for name in repo.get_device_names()], kind=Kind.normal, lazy=False),
        doc="all quadrupoles ",
        default_read_attrs=(),
    )

    power_converter_names = Cpt(
        Signal, name="steerer_names", value=repo.get_device_names(), kind=Kind.config
    )

    sel = Cpt(SelectedPowerConverter, name="sel_pc")

    _default_config_attrs = ("steerer_names",)
    _default_read_attrs = ("sel",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # put default value from repo
        for name in self.power_converter_names.get():
            conf = repo.get(name)
            pc = getattr(self.power_converters, name)
            d = dict(slope=conf.conversion.slope, offset=conf.conversion.intercept)
            pc.configure(d)


if __name__ == "__main__":
    steerer_muxer = SteererCollection(name="sc")
    steerer_muxer
    print("steerer_muxer imported")