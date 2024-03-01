import logging

from bact_bessyii_mls_ophyd.devices.utils.power_converters_as_multiplexer import MultiplexerSetMixin, \
    ScaledPowerConverter, SelectedPowerConverter
from bact_bessyii_ophyd.devices.interfaces.configuration_repository import ConfigurationRepositoryInterface
from .steerer_configuration_repository import ConfigurationRepository
from ophyd import Component as Cpt, Device, DynamicDeviceComponent as DDC, Kind, Signal
from ophyd.areadetector import ad_group

logger = logging.getLogger("bact-bessyii-ophyd")
repo = ConfigurationRepository()


def configure_scaling_power_converters(power_converters, repository: ConfigurationRepositoryInterface):
    """set offset and scale for all power converters given by their names

    Args:
        power_converters:
        repository:
    """
    for name in repo.get_device_names():
        conf = repo.get(name)
        try:
            pc = getattr(power_converters, name)
        except AttributeError as exc:
            logger.warning("Could not configure device %s: reason: %s", name, exc)
            continue

        d = dict(slope=conf.conversion.slope, offset=conf.conversion.intercept)
        pc.configure(d)


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
        configure_scaling_power_converters(self.power_converters, repo)


if __name__ == "__main__":
    steerer_muxer = SteererCollection(name="sc")