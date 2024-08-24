from datetime import datetime, UTC

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False
    )
