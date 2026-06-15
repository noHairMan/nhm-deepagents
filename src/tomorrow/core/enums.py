from enum import Enum, EnumMeta
from typing import Optional, Union


class ChoicesMeta(EnumMeta):
    def __contains__(cls, member: object) -> bool:
        if isinstance(member, Enum):
            return super().__contains__(member)
        return member in cls.values

    @property
    def choices(cls) -> list[tuple[Union[str, int], str]]:
        return [(item.value, item.label) for item in cls]

    @property
    def values(cls) -> list[Union[str, int]]:
        return [item.value for item in cls]

    @property
    def labels(cls) -> list[str]:
        return [item.label for item in cls]


class Choices(Enum, metaclass=ChoicesMeta):
    def __new__(cls, value: Union[str, int], label: Optional[str] = None) -> Choices:
        if issubclass(cls, int):
            obj = int.__new__(cls, value)
        elif issubclass(cls, str):
            obj = str.__new__(cls, value)
        else:
            obj = object.__new__(cls)
        obj._value_ = value
        obj._label = label or value
        return obj

    @property
    def label(self) -> str:
        return self._label


class IntChoices(int, Choices):
    pass


class TextChoices(str, Choices):
    pass
