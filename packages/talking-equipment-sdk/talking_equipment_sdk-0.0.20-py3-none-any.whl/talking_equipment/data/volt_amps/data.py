from dataclasses import dataclass
from typing import Union

from ..data import Data
from ..enums import DataValueType
from ..mixins import UnitConversionMixin
from ..three_phase.data import ThreePhaseDataContainer


@dataclass
class VoltAmpsData(Data, UnitConversionMixin):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit: str = 'Volt Amps'
    unit_abbreviation: str = 'VA'

    def __post_init__(self):
        self.value = float(self.value)


@dataclass(kw_only=True)
class ThreePhaseVoltAmpsData(ThreePhaseDataContainer):
    a: Union[VoltAmpsData, float, int]
    b: Union[VoltAmpsData, float, int]
    c: Union[VoltAmpsData, float, int]

    def __post_init__(self):
        self.a = VoltAmpsData(self.a) if not isinstance(self.a, VoltAmpsData) else self.a
        self.b = VoltAmpsData(self.b) if not isinstance(self.b, VoltAmpsData) else self.b
        self.c = VoltAmpsData(self.c) if not isinstance(self.c, VoltAmpsData) else self.c


@dataclass
class VoltAmpsReactiveData(VoltAmpsData):
    unit = 'Volt Amps Reactive'
    unit_abbreviation = 'VAR'


@dataclass(kw_only=True)
class ThreePhaseVoltAmpsReactiveData(ThreePhaseDataContainer):
    a: Union[VoltAmpsReactiveData, float, int]
    b: Union[VoltAmpsReactiveData, float, int]
    c: Union[VoltAmpsReactiveData, float, int]

    def __post_init__(self):
        self.a = VoltAmpsReactiveData(self.a) if not isinstance(self.a, VoltAmpsReactiveData) else self.a
        self.b = VoltAmpsReactiveData(self.b) if not isinstance(self.b, VoltAmpsReactiveData) else self.b
        self.c = VoltAmpsReactiveData(self.c) if not isinstance(self.c, VoltAmpsReactiveData) else self.c

