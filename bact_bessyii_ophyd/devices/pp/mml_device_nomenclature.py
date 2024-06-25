from dataclasses import dataclass
from typing import Sequence


@dataclass
class DeviceName:
    func_name: str
    cell_id: int
    cell_index: int

class Repo:
    def get(self, function_id) -> Sequence[DeviceName]:
        pass


def foo()
    [, filter(lambda elem: "bpm" in elem.tags, lattice)]