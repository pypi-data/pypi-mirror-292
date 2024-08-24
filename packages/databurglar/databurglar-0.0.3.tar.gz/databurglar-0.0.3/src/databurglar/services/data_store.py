from sqlalchemy import Engine

from ..models.data import Data
from ..models.events import AbstractEvent


class CreationService:
    def __init__(self, engine: Engine):
        pass

    def create(self, data: Data[AbstractEvent]) -> None:
        pass
