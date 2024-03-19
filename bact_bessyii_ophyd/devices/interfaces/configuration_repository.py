from abc import ABCMeta, abstractmethod
from typing import Sequence


class ConfigurationRepositoryInterface(metaclass=ABCMeta):
    @abstractmethod
    def get(self, device_id: str):
        """Should return a data model I suppose
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_names(self) -> Sequence[str]:
        """

        Returns: all known device names

        """
        raise NotImplementedError