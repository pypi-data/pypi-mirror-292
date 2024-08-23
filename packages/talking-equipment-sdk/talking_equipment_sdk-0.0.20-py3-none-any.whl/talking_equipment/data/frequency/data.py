from dataclasses import dataclass
from typing import Union

from ..data import Data, DataContainer
from ..mixins import UnitConversionMixin
from ..enums import DataValueType


@dataclass
class FrequencyData(Data, UnitConversionMixin):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit: str = 'Hertz'
    unit_abbreviation: str = 'Hz'

    def __post_init__(self):
        self.value = float(self.value)