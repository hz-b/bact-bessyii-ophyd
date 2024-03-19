from dataclasses import dataclass
from typing import Sequence


@dataclass
class LinearScaling:
    slope : float
    intercept : float


@dataclass
class SteererConversionModel:
    # name to apply it to
    name : str
    conversion : LinearScaling


@dataclass
class SteerersConversions:
    # rename to elements if more general
    steerers : Sequence[SteererConversionModel]
