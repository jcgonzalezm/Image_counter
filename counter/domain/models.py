from dataclasses import dataclass
from typing import List
from enum import Enum, auto

@dataclass
class Box:
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass
class Prediction:
    class_name: str
    score: float
    box: Box


@dataclass
class ObjectCount:
    object_class: str
    count: int


@dataclass
class CountResponse:
    current_objects: List[ObjectCount]
    total_objects: List[ObjectCount]


class Models(Enum):
    OBJECT_IDENTIFIER = auto()
    CAT_BREED = auto()
    CAT_BREED_COLOR = auto()
    FAKE = auto()

class ObjectsClassNamesTriggers(Enum):
    def available_triggers():
        return  {'cat': Models.CAT_BREED,
                'grey_cat': Models.CAT_BREED_COLOR}
