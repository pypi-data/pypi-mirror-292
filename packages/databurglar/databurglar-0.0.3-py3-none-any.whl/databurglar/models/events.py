from typing import TypeVar
import uuid

from datetime import datetime
from sqlalchemy import UUID, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AbstractEvent(Base):
    __tablename__ = 'event'
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(125))


TEvent = TypeVar('TEvent', bound=AbstractEvent)


class UserEvent(AbstractEvent):
    __table_args__ = (
        UniqueConstraint('user_id', 'label', 'timestamp'),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP)
