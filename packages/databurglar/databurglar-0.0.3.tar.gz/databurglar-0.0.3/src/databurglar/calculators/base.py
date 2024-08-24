from abc import ABC, abstractmethod
from typing import Set

from ..models import DataByCode, Calculation


class AbstractCalculator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def codes(self) -> Set[str]:
        pass

    @abstractmethod
    def calculate(self, data_by_code: DataByCode) -> Calculation:
        pass
