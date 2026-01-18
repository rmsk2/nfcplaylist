from smartcard.util import toHexString
import consts
import uid_reader


class UidReader(uid_reader.IUidReader):
    def __init__(self, watched_atr, card_name = "Ntag215"):
        self._atr = watched_atr
        self._name = card_name
        # https://www.acs.com.hk/download-manual/419/API-ACR122U-2.04.pdf
        self._apdu_get_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    
    def get_atr(self):
        return self._atr
    
    def get_name(self):
        return self._name

    def make_card_id(self, card):
        uid = self._read_ntag_uid(card)
        if uid == None:
            return consts.NO_CARD_ID, False

        new_id = uid_reader.IUidReader.determine_id(bytes(uid))

        return new_id, True

    def _read_ntag_uid(self, card):
        try:
            card.connection = card.createConnection()
            card.connection.connect()
            response, sw1, sw2 = card.connection.transmit(self._apdu_get_uid)
            if (sw1 != 0x90) or (sw2 != 0x00):
                return None

            res = response
        except:
            res = None

        return res
