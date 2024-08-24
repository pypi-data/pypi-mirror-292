import uuid

from typing import Set
from sqlalchemy import Select, select

from ..models import DataStore


class ByIds:
    @staticmethod
    def generate(ids: Set[uuid.UUID]) -> Select:
        return select(DataStore).where(
            DataStore.id.in_(ids)
        )


class ByEvents:
    @staticmethod
    def generate(event_ids: Set[uuid.UUID]) -> Select:
        return select(DataStore).where(
            DataStore.event_id.in_(event_ids)
        )


class ByEventAndTags:
    @staticmethod
    def generate(event_id: uuid.UUID, tags: Set[uuid.UUID]) -> Select:
        return select(DataStore).where(
            (DataStore.event_id == event_id) &
            (DataStore.tag_id.in_(tags))
        )
