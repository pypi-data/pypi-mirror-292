from dataclasses import dataclass
from typing import Union

from ..data import Data
from ..enums import DataValueType
from ..three_phase.data import ThreePhaseDataContainer


@dataclass
class TotalHarmonicDistortionData(Data):
    value: Union[float, int]
    value_type: DataValueType = DataValueType.FLOAT
    unit: str = 'Total Harmonic Distortion'
    unit_abbreviation: str = 'THD'

    def __post_init__(self):
        self.value = float(self.value)


@dataclass(kw_only=True)
class ThreePhaseTotalHarmonicDistortionData(ThreePhaseDataContainer):
    a: Union[TotalHarmonicDistortionData, float, int]
    b: Union[TotalHarmonicDistortionData, float, int]
    c: Union[TotalHarmonicDistortionData, float, int]

    def __post_init__(self):
        self.a = TotalHarmonicDistortionData(self.a) if not isinstance(self.a, TotalHarmonicDistortionData) else self.a
        self.b = TotalHarmonicDistortionData(self.b) if not isinstance(self.b, TotalHarmonicDistortionData) else self.b
        self.c = TotalHarmonicDistortionData(self.c) if not isinstance(self.c, TotalHarmonicDistortionData) else self.c