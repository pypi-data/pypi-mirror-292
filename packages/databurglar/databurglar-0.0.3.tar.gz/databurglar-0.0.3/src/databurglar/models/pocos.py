from dataclasses import dataclass
from typing import Union

from .typings import DataReturnType


@dataclass
class Measurement:
    value: DataReturnType | None
    units: str


@dataclass
class Calculation:
    value: Union[DataReturnType, Measurement] | None
    code: str
