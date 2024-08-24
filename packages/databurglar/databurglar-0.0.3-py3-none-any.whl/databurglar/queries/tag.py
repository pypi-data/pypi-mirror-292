import uuid

from typing import Set
from sqlalchemy import Select, select

from ..models import Tag


class ByIds:
    @staticmethod
    def generate(ids: Set[uuid.UUID]) -> Select:
        return select(Tag).where(
            Tag.id.in_(ids)
        )


class ByCodes:
    @staticmethod
    def generate(codes: Set[str]) -> Select:
        return select(Tag).where(
            Tag.code.in_(codes)
        )
