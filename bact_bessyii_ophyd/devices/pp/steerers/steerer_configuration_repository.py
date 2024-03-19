import json
from pathlib import Path
from typing import Sequence

import jsons

from .conversion_model import SteerersConversions
from ...interfaces.configuration_repository import ConfigurationRepositoryInterface

repo_file = Path(__file__).parent / "steerer_conversions.json"


class ConfigurationRepository(ConfigurationRepositoryInterface):
    def __init__(self):
        with open(repo_file) as fp:
            tmp = json.load(fp)

        tmp = jsons.load(tmp, SteerersConversions)
        self.repo = {entry.name: entry for entry in tmp.steerers}

    def get(self, device_id: str):
        return self.repo[device_id]

    def get_device_names(self) -> Sequence[str]:
        return [name for name in self.repo.keys() if name[:3] != "VS4"]
        return list(self.repo.keys())


if __name__ == "__main__":
    c = ConfigurationRepository()
    c
