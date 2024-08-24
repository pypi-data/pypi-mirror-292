from typing import Union

import uuid
import datetime

from sqlalchemy import String, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


DataReturnType = Union[str, float, datetime.date, bool]


class Survey(Base):
    __tablename__ = 'survey'
    __table_args__ = (
        UniqueConstraint('code'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str | None] = mapped_column(String(250), nullable=True)
