from dataclasses import dataclass
from typing import Optional

from ..current.data import CurrentData, ThreePhaseCurrentData
from ..data import DataContainer
from ..frequency.data import FrequencyData
from ..power_factor.data import PowerFactorData, ThreePhasePowerFactorData
from ..total_harmonic_distortion.data import TotalHarmonicDistortionData
from ..voltage.data import VoltageData, ThreePhaseVoltageData
from ..volt_amps.data import VoltAmpsData, ThreePhaseVoltAmpsData, VoltAmpsReactiveData, ThreePhaseVoltAmpsReactiveData
from ..watts.data import WattsData, ThreePhaseWattsData


@dataclass(kw_only=True)
class _PowerMeterData(DataContainer):
    frequency: Optional[FrequencyData] = None
    total_voltamps_reactive: Optional[VoltAmpsReactiveData] = None
    total_apparent_power: Optional[WattsData] = None
    total_power_factor: Optional[PowerFactorData] = None
    total_system_power: Optional[WattsData] = None
    total_harmonic_distortion: Optional[TotalHarmonicDistortionData] = None
    neutral_current: Optional[CurrentData] = None


@dataclass(kw_only=True)
class SinglePhasePowerMeterData(_PowerMeterData):
    current: Optional[CurrentData] = None
    power_factor: Optional[PowerFactorData] = None
    voltage: Optional[VoltageData] = None
    voltamps: Optional[VoltAmpsData] = None
    voltamps_reactive: Optional[VoltAmpsReactiveData] = None
    watts: Optional[WattsData] = None


@dataclass(kw_only=True)
class ThreePhasePowerMeterData(_PowerMeterData):
    current: Optional[ThreePhaseCurrentData] = None
    power_factor: Optional[ThreePhasePowerFactorData] = None
    voltage: Optional[ThreePhaseVoltageData] = None
    voltamps: Optional[ThreePhaseVoltAmpsData] = None
    voltamps_reactive: Optional[ThreePhaseVoltAmpsReactiveData] = None
    watts: Optional[ThreePhaseWattsData] = None

