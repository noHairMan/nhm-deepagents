from enum import Enum, EnumMeta
from typing import Any, List, Optional, Tuple


class ChoicesMeta(EnumMeta):
    def __contains__(cls, member: Any) -> bool:
        if isinstance(member, Enum):
            return super().__contains__(member)
        return member in cls.values

    @property
    def choices(cls) -> List[Tuple[Any, str]]:
        return [(item.value, item.label) for item in cls]

    @property
    def values(cls) -> List[Any]:
        return [item.value for item in cls]

    @property
    def labels(cls) -> List[str]:
        return [item.label for item in cls]


class Choices(Enum, metaclass=ChoicesMeta):
    def __new__(cls, value: Any, label: Optional[str] = None) -> "Choices":
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
