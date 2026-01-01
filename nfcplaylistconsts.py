import hashlib
from typing import Any

# Function codes
FUNC_PLAYLIST_RESTART = 0
FUNC_SONG_RESTART = 1
FUNC_END = 2
FUNC_PERFORMED = 3
FUNC_SONG_SKIP = 4
FUNC_SONG_PREV = 5

# Error codes
ERR_TYPE_COMM = 1
ERR_TYPE_FILE = 2

# ATRs of known card types
ATR_DES_FIRE = "3B 81 80 01 80 80"
ATR_E_PERSO = "3B 84 80 01 80 82 90 00 97"
ATR_GIRO = "3B 87 80 01 80 31 C0 73 D6 31 C0 23"
ATR_EGK = "3B 85 80 01 30 01 01 30 30 34"
ATR_NTAG = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 03 00 00 00 00 68"
ATR_MIFARE_CLASSIC = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"
ALL_ATRS = [ATR_E_PERSO, ATR_GIRO, ATR_EGK, ATR_DES_FIRE, ATR_NTAG, ATR_MIFARE_CLASSIC]

# Change to cls on Windows
CLEAR_COMMAND = 'clear'
# Change this in order to shutdown the computer when nfcplaylist ends.
# For use on macOS
# SHUTDOWN_COMMAND = "sudo shutdown -h now"
SHUTDOWN_COMMAND = "echo shutdown"

# This should be as long as the longest string to be displayed
EMPTY_STR = '                                  '
ERR_MSG_LOAD_PLAYLIST = "err_msg_load_playlist"
STD_MSG = "std_msg"
CAPTION_DEFAULT = "caption_default"
ERR_MSG_LOAD_CONFIG = "err_msg_load_config"
MSG_PLAYLIST_BEGINING = "msg_playlist_beginning"
MSG_RESTART_SONG = "msg_restart_song"
MSG_SKIP_SONG = "msg_skip_song"
MSG_NEXT_SONG = "msg_next_song"
MSG_SHUTDOWN = "msg_shutdown"
MSG_PLAY_FORMAT_STR = "msg_play_format_str"

all_messages = {
    ERR_MSG_LOAD_PLAYLIST: "Unable to load playlists",
    STD_MSG: "Hello",
    CAPTION_DEFAULT: "Simple audio book player",
    ERR_MSG_LOAD_CONFIG: "Unable to load configuration",
    MSG_PLAYLIST_BEGINING: "Go back to beginning of audio book",
    MSG_RESTART_SONG: "Go back to beginning of chapter",
    MSG_SKIP_SONG: "To next chapter",
    MSG_NEXT_SONG: "To previous chapter",
    MSG_PLAY_FORMAT_STR: "Chapter {song} of {num_songs}",
    MSG_SHUTDOWN: "Good bye!"
}

NO_CARD_ID = -1
NO_ATR = ""


def set_lang_ger():
    all_messages[ERR_MSG_LOAD_PLAYLIST] = "Playlist konnte nicht geladen werden"
    all_messages[STD_MSG] = "Hallo"
    all_messages[CAPTION_DEFAULT] = "Einfacher Hörbuchspieler"
    all_messages[ERR_MSG_LOAD_CONFIG] = "Konfigrationsdatei konnte nicht gelesen werden"
    all_messages[MSG_PLAYLIST_BEGINING] = "Zum Anfang des Hörbuchs"
    all_messages[MSG_RESTART_SONG] = "Zum Anfang des Kapitels"
    all_messages[MSG_SKIP_SONG] = "Zum nächsten Kapitel"
    all_messages[MSG_NEXT_SONG] = "Zum vorigen Kapitel"
    all_messages[MSG_PLAY_FORMAT_STR] = "Kapitel {song} von {num_songs}"
    all_messages[MSG_SHUTDOWN] = "Auf Wiedersehen!"


def set_shutdown_command(cmd):
    global SHUTDOWN_COMMAND
    SHUTDOWN_COMMAND = cmd


def get_shutdown_command():
    return SHUTDOWN_COMMAND


def get_clear_command():
    return CLEAR_COMMAND


def set_message(key, value):
    all_messages[key] = value


# A UiReader knows how to calculate an individual identity for
# the cards of a specifc type using their serial number
class IUidReader:
    def make_card_id(self, card: Any) -> tuple[int, bool]:
        # id, ok
        return NO_CARD_ID, False

    def get_atr(self) -> str:
        return NO_ATR

    def get_name(self) -> str:
        return ""

    @staticmethod
    def determine_id(data: bytes) -> int:
        t = hashlib.md5(data).digest()[0:2]
        return t[1]*256 + t[0]
