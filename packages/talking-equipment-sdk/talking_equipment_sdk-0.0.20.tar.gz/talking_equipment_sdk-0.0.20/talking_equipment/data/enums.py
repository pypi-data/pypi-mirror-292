from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Union, Type


class DataValueType(StrEnum):
    INT = 'int'
    FLOAT = 'float'
    STR = 'str'
    BOOL = 'bool'
    JSON = 'json'


@dataclass
class UnitScaleValue:
    scale: Union[int, float]
    abbreviation: str


USV = UnitScaleValue


class UnitScaleValues(Enum):
    MICRO = USV(0.000_001, 'u')
    MILLI = USV(0.001, 'm')
    KILO = USV(1_000, 'k')
    MEGA = USV(1_000_000, 'M')
    GIGA = USV(1_000_000_000, 'G')
    TERA = USV(1_000_000_000_000, 'T')
    PETA = USV(1_000_000_000_000_000, 'P')
    EXA = USV(1_000_000_000_000_000_000, 'E')

    @property
    def scale(self):
        return self._value_.scale

    @property
    def abbreviation(self):
        return self._value_.abbreviation