from typing import Dict, cast

from .base import AbstractTagValidator
from ..models import DataReturnType, Tag


class TagValidatorService:
    def __init__(self) -> None:
        self._validators: Dict[str, AbstractTagValidator] = {}

    def add(self, validator: AbstractTagValidator) -> None:
        self._validators[validator.name] = validator

    def validate(self, tag: Tag, value: DataReturnType | None) -> bool:
        for key in tag.validators:
            if key not in self._validators:
                continue

            validator = cast(AbstractTagValidator, self._validators.get(key))
            if not validator.is_valid(tag, value):
                return False

        return True
