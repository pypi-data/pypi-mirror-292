from dataclasses import dataclass
from typing import Union

from ..current.data import CurrentData
from ..data import Data
from ..enums import DataValueType
from ..mixins import UnitConversionMixin
from ..three_phase.data import ThreePhaseDataContainer
from ..voltage.data import VoltageData


@dataclass
class WattsData(Data, UnitConversionMixin):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit: str = 'Watts'
    unit_abbreviation: str = 'W'

    def __post_init__(self):
        self.value = float(self.value)

    def to_voltage(self, current: CurrentData) -> float:
        return self.value / current.value

    def to_current(self, voltage: VoltageData) -> float:
        return self.value / voltage.value

    def set_from_voltage_and_current(self, voltage: VoltageData, current: CurrentData):
        self.value = voltage.value * current.value


@dataclass(kw_only=True)
class ThreePhaseWattsData(ThreePhaseDataContainer):
    a: Union[WattsData, float, int]
    b: Union[WattsData, float, int]
    c: Union[WattsData, float, int]

    def __post_init__(self):
        self.a = WattsData(self.a) if not isinstance(self.a, WattsData) else self.a
        self.b = WattsData(self.b) if not isinstance(self.b, WattsData) else self.b
        self.c = WattsData(self.c) if not isinstance(self.c, WattsData) else self.c


@dataclass
class WattHoursData(WattsData):
    unit: str = 'Watt Hours'
    unit_abbreviation: str = 'Wh'


@dataclass
class ThreePhaseWattHoursData(ThreePhaseDataContainer):
    a: Union[WattHoursData, float, int]
    b: Union[WattHoursData, float, int]
    c: Union[WattHoursData, float, int]

    def __post_init__(self):
        self.a = WattHoursData(self.a) if not isinstance(self.a, WattHoursData) else self.a
        self.b = WattHoursData(self.b) if not isinstance(self.b, WattHoursData) else self.b
        self.c = WattHoursData(self.c) if not isinstance(self.c, WattHoursData) else self.c