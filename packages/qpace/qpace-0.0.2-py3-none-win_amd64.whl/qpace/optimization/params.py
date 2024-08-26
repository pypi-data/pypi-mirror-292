import abc
import itertools
from typing import Any
from ..utils import clamp


class Param(abc.ABC):
    @abc.abstractmethod
    def __init__(self, dtype: str = None):
        self.dtype = dtype

    @staticmethod
    def number():
        return NumParam()

    @staticmethod
    def choice():
        return ChoiceParam()

    @staticmethod
    def bool():
        return BoolParam()


class NumParam(Param):
    DTYPE = "num"

    def __init__(self):
        super().__init__(dtype=self.DTYPE)
        self.min = None
        self.max = None
        self.step = None

    def set_range(self, min: float, max: float, step: float):
        self.min = min
        self.max = max
        self.step = step
        return self

    def from_float(self, value: float):
        return clamp(value, self.min, self.max)

    def into_float_list(self) -> list[float]:
        x = []
        current = self.min
        while current <= self.max:
            x.append(current)
            current += self.step
        return x


class ChoiceParam(Param):
    DTYPE = "choice"

    def __init__(self):
        super().__init__(dtype=self.DTYPE)
        self.choices = []

    def add_choice(self, value):
        self.choices.append(value)
        return self

    def from_float(self, value: float):
        return self.choices[int(value)]

    def into_float_list(self) -> list[float]:
        return list(range(len(self.choices)))


class BoolParam(Param):
    DTYPE = "bool"

    def __init__(self):
        super().__init__(dtype=self.DTYPE)

    def from_float(self, value: float):
        return bool(int(value))

    def into_float_list(self) -> list[float]:
        return [0, 1]


def stringify_params_dict(params: dict[str, Any]) -> str:
    return ", ".join(f"{k}={v}" for k, v in params.items())
