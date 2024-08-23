from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Union

from ..data import Data, DataContainer


@dataclass(kw_only=True)
class ThreePhaseDataContainer(DataContainer):
    a: Data
    b: Data
    c: Data

    @abstractmethod
    def __post_init__(self):
        ...

    @property
    def avg(self) -> Union[float, int]:
        return self.average

    @property
    def average(self) -> Union[float, int]:
        return (self.a.value + self.b.value + self.c.value) / 3

    @property
    def min(self) -> Union[float, int]:
        return self.minimum

    @property
    def minimum(self) -> Union[float, int]:
        return min(self.a.value, self.b.value, self.c.value)

    @property
    def max(self) -> Union[float, int]:
        return self.maximum

    @property
    def maximum(self) -> Union[float, int]:
        return max(self.a.value, self.b.value, self.c.value)

