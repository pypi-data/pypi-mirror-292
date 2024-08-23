from dataclasses import dataclass

from ..data import Data
from ..enums import DataValueType


@dataclass
class ControlData(Data):
    value: str
    value_type: DataValueType = DataValueType.STR
    unit: str = 'Control'
    unit_abbreviation: str = 'CTRL'

    key: str = 'RelayState1|RelayState2'

    @property
    def values(self) -> list:
        return self.value.split('|')

    @property
    def keys(self) -> list:
        return self.key.split('|')

    def as_dict(self) -> dict:
        return dict(zip(self.keys, self.values))
