from smartcard.util import toHexString
from typing import Any
import consts
import uid_reader
import desfire
import iso14443

class AtrReader(uid_reader.IUidReader):
    def __init__(self, name, atr):
        self._id = UidReaderRepo.get_default_id(atr)
        self._name = name
        self._atr = atr

    def make_card_id(self, card: Any) -> tuple[int, bool]:
        return self._id, True

    def get_atr(self) -> str:
        return self._atr

    def get_name(self) -> str:
        return self._name


class UidReaderRepo:
    def __init__(self):
        self._atr_map = {}
        self.add_named_cards()

        # automatically create an ATR uid reader for all cards which are
        # not explicitly named
        all = set(consts.ALL_ATRS)
        named = set(self._atr_map.keys())
        not_named = all - named        

        for i in not_named:
            card_type = UidReaderRepo.get_default_id(i)
            self._atr_map[i] = AtrReader(f"Type {card_type}", i)

    def add_named_cards(self):
        self._atr_map[consts.ATR_DES_FIRE] = desfire.UidReader(consts.ATR_DES_FIRE)
        self._atr_map[consts.ATR_NTAG] = iso14443.UidReader(consts.ATR_NTAG)
        self._atr_map[consts.ATR_MIFARE_CLASSIC] = iso14443.UidReader(consts.ATR_MIFARE_CLASSIC, "Mifare Classic")
        self._atr_map[consts.ATR_MIFARE_ULTRALIGHT] = iso14443.UidReader(consts.ATR_MIFARE_ULTRALIGHT, "Mifare Ultralight")
        self._atr_map[consts.ATR_E_PERSO] = AtrReader("German national ID", consts.ATR_E_PERSO)
        self._atr_map[consts.ATR_GIRO] = AtrReader("German Giro", consts.ATR_GIRO)
        self._atr_map[consts.ATR_EGK] = AtrReader("German electronic health", consts.ATR_EGK)

    @staticmethod
    def get_default_id(atr):
        index = 0
        for i in consts.ALL_ATRS:
            if i == atr:
                return index
            else:
                index += 1
        
        raise Exception(f"Unknown ATR {atr}")

    def to_uid_r(self, atr):
        if atr in self._atr_map.keys():
            return self._atr_map[atr]
        else:
            raise Exception(f"Unknown ATR {atr}")