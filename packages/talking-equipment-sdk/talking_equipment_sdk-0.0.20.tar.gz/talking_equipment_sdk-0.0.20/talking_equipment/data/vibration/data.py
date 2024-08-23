from dataclasses import dataclass

from ..data import Data
from ..enums import DataValueType


@dataclass
class VibrationData(Data):
    value: str
    value_type: DataValueType = DataValueType.STR
    unit: str = 'Vibration'
    unit_abbreviation: str = 'VIBR'

    key: str = 'X-Axis Speed|Y-Axis Speed|Z-Axis Speed|X-Axis Frequency|Y-Axis Frequency|Z-Axis Frequency|Duty Cycle'

    @property
    def values(self) -> list:
        return self.value.split('|')

    @property
    def keys(self) -> list:
        return self.key.split('|')

    def as_dict(self) -> dict:
        return dict(zip(self.keys, self.values))