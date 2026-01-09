import hashlib
from typing import Any
import consts

# A UiReader knows how to calculate an individual identity for
# the cards of a specifc type using their serial number
class IUidReader:
    def make_card_id(self, card: Any) -> tuple[int, bool]:
        # id, ok
        return consts.NO_CARD_ID, False

    def get_atr(self) -> str:
        return consts.NO_ATR

    def get_name(self) -> str:
        return ""

    @staticmethod
    def determine_id(data: bytes) -> int:
        t = hashlib.md5(data).digest()[0:2]
        return t[1]*256 + t[0]