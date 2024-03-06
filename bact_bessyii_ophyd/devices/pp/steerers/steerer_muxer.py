from __future__ import annotations
import logging
from typing import Sequence

from  bact_bessyii_mls_ophyd.devices.utils import power_converters_as_multiplexer
print(power_converters_as_multiplexer)

from bact_bessyii_mls_ophyd.devices.utils.power_converters_as_multiplexer import (
    MultiplexerSetMixin,
    ScaledPowerConverter,
    SelectedPowerConverter,
)
from bact_bessyii_ophyd.devices.interfaces.configuration_repository import (
    ConfigurationRepositoryInterface,
)
from .steerer_configuration_repository import ConfigurationRepository
from ophyd import Component as Cpt, Device, DynamicDeviceComponent as DDC, Kind, Signal
from ophyd.areadetector import ad_group

logger = logging.getLogger("bact-bessyii-ophyd")
repo = ConfigurationRepository()


def configure_scaling_power_converter(
    power_converter, repository,
    name: str
):
    try:
        conf = repository.get(name)
    except AttributeError as exc:
        logger.warning("Could not retrieve configuration of device %s: reason: %s", name, exc)
        raise exc

    power_converter.configure(dict(slope=conf.conversion.slope, offset=conf.conversion.intercept))


class SteerersCollection(Device, MultiplexerSetMixin):
    """Steerers with scaling to value"""

    power_converters = DDC(
        ad_group(
            ScaledPowerConverter,
            [(name, name) for name in repo.get_device_names()],
            kind=Kind.normal,
            lazy=False,
        ),
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
        for name in self.get_element_names():
            pc = self.get_steerer_by_name(name)
            configure_scaling_power_converter(pc, repo, name)

    def get_element_names(self):
        return self.power_converter_names.get()

    def get_steerer_by_name(self, name: str):
        return getattr(self.power_converters, name)

if __name__ == "__main__":
    steerer_muxer = SteerersCollection(name="sc")
