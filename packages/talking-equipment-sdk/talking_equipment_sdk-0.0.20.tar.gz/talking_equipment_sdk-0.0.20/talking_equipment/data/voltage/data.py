from dataclasses import dataclass
from typing import Union, get_type_hints

from ..data import Data
from ..three_phase.data import ThreePhaseDataContainer
from ..enums import DataValueType
from ..mixins import UnitConversionMixin


@dataclass
class VoltageData(Data, UnitConversionMixin):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit_name: str = 'Volts'
    unit_abbreviation: str = 'V'

    def __post_init__(self):
        self.value = float(self.value)

    def __str__(self):
        return self.auto_scale_verbose


@dataclass(kw_only=True)
class ThreePhaseVoltageData(ThreePhaseDataContainer):
    a: Union[VoltageData, float, int]
    b: Union[VoltageData, float, int]
    c: Union[VoltageData, float, int]

    def __post_init__(self):
        self.a = VoltageData(self.a) if not isinstance(self.a, VoltageData) else self.a
        self.b = VoltageData(self.b) if not isinstance(self.b, VoltageData) else self.b
        self.c = VoltageData(self.c) if not isinstance(self.c, VoltageData) else self.c
