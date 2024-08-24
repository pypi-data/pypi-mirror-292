from typing import List

import uuid

from sqlalchemy import Enum, String, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects import postgresql as pg

from .base import Base
from .enums import DataType


class Tag(Base):
    __tablename__ = 'tag'
    __table_args__ = (
        UniqueConstraint('code'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    data_type: Mapped[DataType] = mapped_column(Enum(DataType), nullable=False)
    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(125))
    units: Mapped[str] = mapped_column(String(15), nullable=True)
    validators: Mapped[List[str]] = mapped_column(
        pg.ARRAY(String(125)),
        default=list
    )

    @property
    def is_measurement(self) -> bool:
        return self.units not in ('', None)
