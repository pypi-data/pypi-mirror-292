from typing import Dict, List
import uuid
import datetime

from sqlalchemy import DATE, TEXT, ForeignKey, FLOAT, BOOLEAN, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects import postgresql as pg


from .base import Base
from .enums import DataType
from .typings import DataReturnType
from .pocos import Measurement
from .tag import Tag


class TaggedData(Base):
    __abstract__ = True

    tag_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('tag.id'))
    text: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    number: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    date: Mapped[datetime.date | None] = mapped_column(DATE, nullable=True)
    boolean: Mapped[bool | None] = mapped_column(BOOLEAN, nullable=True)
    complex: Mapped[dict | None] = mapped_column(pg.JSON, nullable=True)
    is_valid: Mapped[bool] = mapped_column(BOOLEAN, default=False)

    def get_value(self, tag: Tag) -> DataReturnType | None:
        if tag.data_type == DataType.NUMBER:
            return self.number

        if tag.data_type == DataType.TEXT:
            return self.text

        if tag.data_type == DataType.DATE:
            return self.date

        if tag.data_type == DataType.BOOLEAN:
            return self.boolean

        if tag.data_type == DataType.COMPLEX:
            return self.complex

        return None

    def get_measurement(self, tag: Tag) -> Measurement | None:
        if tag.is_measurement:
            return Measurement(
                value=self.get_value(tag),
                units=tag.units
            )

        return None


class DataStore(TaggedData):
    __tablename__ = 'data_store'
    __table_args__ = (
        UniqueConstraint('event_id', 'tag_id'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('event.id'))


class DataByCode:
    def __init__(self, data: Dict[str, List[DataStore]]) -> None:
        self._data = data

    def get(self, code: str) -> List[DataStore]:
        return self._data.get(code, [])
