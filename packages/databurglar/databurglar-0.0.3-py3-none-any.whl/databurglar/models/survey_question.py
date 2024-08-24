import uuid

from sqlalchemy import TEXT, ForeignKey, UniqueConstraint, UUID, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SurveyQuestion(Base):
    __tablename__ = 'survey_question'
    __table_args__ = (
        UniqueConstraint('survey_id', 'tag_id'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    survey_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('survey.id'))
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('tag.id'))

    text: Mapped[str] = mapped_column(TEXT)

    is_required: Mapped[bool] = mapped_column(BOOLEAN, default=False)
