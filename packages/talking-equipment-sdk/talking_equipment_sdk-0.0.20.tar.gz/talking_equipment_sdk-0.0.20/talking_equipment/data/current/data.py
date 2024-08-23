from dataclasses import dataclass
from typing import Union

from ..data import Data
from ..enums import DataValueType
from ..mixins import UnitConversionMixin
from ..three_phase.data import ThreePhaseDataContainer


@dataclass
class CurrentData(Data, UnitConversionMixin):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit: str = 'Amps'
    unit_abbreviation: str = 'A'

    def __post_init__(self):
        self.value = float(self.value)


@dataclass(kw_only=True)
class ThreePhaseCurrentData(ThreePhaseDataContainer):
    a: Union[CurrentData, float, int]
    b: Union[CurrentData, float, int]
    c: Union[CurrentData, float, int]

    def __post_init__(self):
        self.a = CurrentData(self.a) if not isinstance(self.a, CurrentData) else self.a
        self.b = CurrentData(self.b) if not isinstance(self.b, CurrentData) else self.b
        self.c = CurrentData(self.c) if not isinstance(self.c, CurrentData) else self.c
