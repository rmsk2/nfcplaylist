import hashlib
from typing import Any
from abc import ABC, abstractmethod

# A UiReader knows how to calculate an individual identity for
# the cards of a specifc type using their serial number
class IUidReader(ABC):
    @abstractmethod
    def make_card_id(self, card: Any) -> tuple[int, bool]:
        # return the tuple (card id, success flag). True means success.
        ...

    @abstractmethod
    def get_atr(self) -> str:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @staticmethod
    def determine_id(data: bytes) -> int:
        t = hashlib.md5(data).digest()[0:2]
        return t[1]*256 + t[0]