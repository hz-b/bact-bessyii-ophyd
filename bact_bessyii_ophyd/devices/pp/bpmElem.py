from dataclasses import dataclass

import numpy as np

import jsons


@dataclass
class BpmElementList:
    def __init__(self):
        self.bpmElemList = []

    def add_bpm_elem(self, bpm_elem):
        self.bpmElemList.append(bpm_elem)

    @staticmethod
    def describe_dict():
        return dict(source="", shape=[32], dtype="array")

    def to_dict(self, timestamp):
        return {'value': self.bpmElemList, 'timestamp': timestamp}

    @staticmethod
    def to_json(data):
        return jsons.dump(data)


@dataclass
class BpmElemPlane:
    pos_raw: float
    rms_raw: float


@dataclass
class BpmElem:

    x: BpmElemPlane
    y: BpmElemPlane
    intensity_z: float
    intensity_s: float
    stat: float
    gain_raw: float
    name: str
