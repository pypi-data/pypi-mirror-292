from dataclasses import dataclass
from typing import Union

from ..data import Data
from ..enums import DataValueType
from ..mixins import UnitConversionMixin
from ..three_phase.data import ThreePhaseDataContainer


@dataclass
class PowerFactorData(Data, UnitConversionMixin):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit: str = 'Power Factor'
    unit_abbreviation: str = 'PF'

    def __post_init__(self):
        self.value = float(self.value)


@dataclass(kw_only=True)
class ThreePhasePowerFactorData(ThreePhaseDataContainer):
    a: Union[PowerFactorData, float, int]
    b: Union[PowerFactorData, float, int]
    c: Union[PowerFactorData, float, int]

    def __post_init__(self):
        self.a = PowerFactorData(self.a) if not isinstance(self.a, PowerFactorData) else self.a
        self.b = PowerFactorData(self.b) if not isinstance(self.b, PowerFactorData) else self.b
        self.c = PowerFactorData(self.c) if not isinstance(self.c, PowerFactorData) else self.c
