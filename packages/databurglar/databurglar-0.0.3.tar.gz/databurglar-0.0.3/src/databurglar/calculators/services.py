from typing import List

from .base import AbstractCalculator
from ..models import Calculation, DataByCode


class CalculatorService:
    def __init__(self) -> None:
        self._calculators: List[AbstractCalculator] = []

    def add(self, calculator: AbstractCalculator) -> None:
        self._calculators.append(calculator)

    def calculate(self, data_by_code: DataByCode) -> List[Calculation]:
        results: List[Calculation] = []

        for calculator in self._calculators:
            results.append(
                calculator.calculate(data_by_code)
            )

        return results
