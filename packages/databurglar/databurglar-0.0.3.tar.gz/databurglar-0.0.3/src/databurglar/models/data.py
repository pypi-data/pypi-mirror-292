from dataclasses import dataclass
from typing import Generic, List

from .events import TEvent
from .data_store import DataStore


@dataclass
class Data(Generic[TEvent]):
    event: TEvent
    items: List[DataStore]
