from dataclasses import dataclass
from typing import Union

from .enums import UnitScaleValues


class UnitConversionMixin:
    def _unit_verbose(
            self,
            value: Union[int, float],
            unit_scale_abbreviation: str
    ) -> str:
        return f'{value}{unit_scale_abbreviation}{self.unit_abbreviation}'

    @property
    def micro(self) -> float:
        return self.value / UnitScaleValues.MICRO.scale

    @property
    def micro_verbose(self) -> str:
        return self._unit_verbose(self.micro, UnitScaleValues.MICRO.abbreviation)

    @property
    def milli(self) -> float:
        return self.value / UnitScaleValues.MILLI.scale

    @property
    def milli_verbose(self) -> str:
        return self._unit_verbose(self.milli, UnitScaleValues.MILLI.abbreviation)

    @property
    def kilo(self) -> float:
        return self.value / UnitScaleValues.KILO.scale

    @property
    def kilo_verbose(self) -> str:
        return self._unit_verbose(self.kilo, UnitScaleValues.KILO.abbreviation)

    @property
    def mega(self) -> float:
        return self.value / UnitScaleValues.MEGA.scale

    @property
    def mega_verbose(self) -> str:
        return self._unit_verbose(self.mega, UnitScaleValues.MEGA.abbreviation)

    @property
    def giga(self) -> float:
        return self.value / UnitScaleValues.GIGA.scale

    @property
    def giga_verbose(self) -> str:
        return self._unit_verbose(self.giga, UnitScaleValues.GIGA.abbreviation)

    @property
    def tera(self) -> float:
        return self.value / UnitScaleValues.TERA.scale

    @property
    def tera_verbose(self) -> str:
        return self._unit_verbose(self.tera, UnitScaleValues.TERA.abbreviation)

    @property
    def peta(self) -> float:
        return self.value / UnitScaleValues.PETA.scale

    @property
    def peta_verbose(self) -> str:
        return self._unit_verbose(self.peta, UnitScaleValues.PETA.abbreviation)

    @property
    def exa(self) -> float:
        return self.value / UnitScaleValues.EXA.scale

    @property
    def exa_verbose(self) -> str:
        return self._unit_verbose(self.exa, UnitScaleValues.EXA.abbreviation)

    @property
    def auto_scale_verbose(self) -> str:
        if self.value > UnitScaleValues.EXA.scale:
            return self.exa_verbose
        elif self.value > UnitScaleValues.PETA.scale:
            return self.peta_verbose
        elif self.value > UnitScaleValues.TERA.scale:
            return self.tera_verbose
        elif self.value > UnitScaleValues.GIGA.scale:
            return self.giga_verbose
        elif self.value > UnitScaleValues.MEGA.scale:
            return self.mega_verbose
        elif self.value > UnitScaleValues.KILO.scale:
            return self.kilo_verbose
        elif self.value >= 0:
            return self.value_verbose
        elif self.value > UnitScaleValues.MILLI.scale:
            return self.milli_verbose
        elif self.value > UnitScaleValues.MICRO.scale:
            return self.micro_verbose
        else:
            return self.value_verbose