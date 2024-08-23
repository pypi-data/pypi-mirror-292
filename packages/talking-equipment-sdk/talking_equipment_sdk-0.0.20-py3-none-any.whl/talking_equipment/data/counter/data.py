from dataclasses import dataclass
from typing import Union

from ..data import Data
from ..enums import DataValueType


@dataclass
class CounterData(Data):
    value: Union[int, float]
    value_type: DataValueType = DataValueType.INT
    unit: str = 'Count'
    unit_abbreviation: str = 'CNT'

    def __post_init__(self):
        self.value = int(self.value)