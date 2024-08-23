import json

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, fields
from enum import Enum
from typing import Any, Union, Type, get_type_hints

from .enums import DataValueType


@dataclass
class BaseData(ABC):

    @classmethod
    @abstractmethod
    def load_from_value(cls, value: Union[float, int, str, bool]):
        pass

    @classmethod
    @abstractmethod
    def load_from_value_dict(cls, value: Union[float, int, str, bool]):
        pass

    @abstractmethod
    def _value_as_dict(self) -> dict:
        pass


@dataclass
class Data(BaseData):
    value: Union[int, float, str]
    value_type: DataValueType = None
    unit_name: str = ''
    unit_abbreviation: str = ''

    def __str__(self):
        return self.value_verbose

    @classmethod
    def load_from_value(cls, value):
        return cls(value=value)

    @classmethod
    def load_from_value_dict(cls, value):
        return cls.load_from_value(value)

    def _value_as_dict(self):
        # TODO: Rename to match as this doesnt always return a dict
        return self.value

    @classmethod
    @property
    def value_type_str(cls) -> str:
        return cls.value_type.__name__

    @property
    def value_verbose(self) -> str:
        return f'{self.value}{self.unit_abbreviation}'

    @property
    def value_verbose_full(self) -> str:
        return f'{self.value} {self.unit_name}'

    @property
    def is_int(self) -> bool:
        return isinstance(self.value, int)

    @property
    def is_bool(self) -> bool:
        return isinstance(self.value, bool)

    @property
    def is_float(self) -> bool:
        return isinstance(self.value, float)

    @property
    def is_json(self) -> bool:
        try:
            json.loads(self.value)
            return True
        except ValueError:
            return False

    @property
    def is_str(self) -> bool:
        return isinstance(self.value, str)


@dataclass(kw_only=True)
class DataContainer(BaseData):
    value_type: DataValueType = DataValueType.JSON

    @classmethod
    def load_from_value(cls, value):
        return cls.load_from_value_dict(json.loads(value))

    @classmethod
    def load_from_value_dict(cls, value: dict):
        loaded_value_dict = {}

        for attribute_name, attribute_type in get_type_hints(cls).items():
            if attribute_name in value:
                loaded_value_dict[attribute_name] = attribute_type.load_from_value_dict(value[attribute_name])

        return cls(**loaded_value_dict)

    @property
    def value(self):
        return json.dumps(self._value_as_dict())

    def _value_as_dict(self) -> dict:
        value_dict = {}
        for key, value in self.__dict__.items():
            if key != 'value_type' and value is not None:
                value_dict[key] = value._value_as_dict()

        return value_dict
