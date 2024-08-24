from abc import ABC, abstractmethod

from ..models import DataReturnType, Tag


class AbstractTagValidator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def is_valid(self, tag: Tag, value: DataReturnType | None) -> bool:
        pass
