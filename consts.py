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
ATR_MIFARE_ULTRALIGHT = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 3D 00 00 00 00 56"
ATR_MIFARE_CLASSIC = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"
ALL_ATRS = [ATR_E_PERSO, ATR_GIRO, ATR_EGK, ATR_DES_FIRE, ATR_NTAG, ATR_MIFARE_CLASSIC, ATR_MIFARE_ULTRALIGHT]

# Change to cls on Windows
CLEAR_COMMAND = 'clear'
# Change this in order to shutdown the computer when nfcplaylist ends.
# For use on macOS
# SHUTDOWN_COMMAND = "sudo shutdown -h now"
SHUTDOWN_COMMAND = "echo shutdown"

NO_CARD_ID = -1
NO_ATR = ""

VERSION_STRING = "1.2.1"

def set_shutdown_command(cmd):
    global SHUTDOWN_COMMAND
    SHUTDOWN_COMMAND = cmd


def get_shutdown_command():
    return SHUTDOWN_COMMAND


def get_clear_command():
    return CLEAR_COMMAND

