import os
import sys
import json
import pygame
import nfcplaylist
import consts


VERSION_STRING = "1.1.0"

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


def set_message(key, value):
    all_messages[key] = value


class NfcPlaylistUI:
    def __init__(self, event_ui_stopped):
        self.stopped_event = event_ui_stopped
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)
        self._x_size = 800
        self._y_size = 600
        self._text = all_messages[STD_MSG]
        self._func_text = EMPTY_STR
        self._background_col = self.white
        self._font_size = 48
        self._func_font_size = 32
        self._logger = self._err_logger
        self._activate_close_button = False

        self._err_map = {
            consts.ERR_TYPE_COMM: self.red,
            consts.ERR_TYPE_FILE: self.blue
        }

    @property
    def card_ids(self):
        return self._ui_config["ids"]

    @property
    def activate_close_button(self):
        return self._activate_close_button

    @property
    def logger(self):
        return self._logger
    
    @logger.setter
    def logger(self, val):
        self._logger = val

    def init(self, config_dir):
        self._load_config(config_dir)

        if ("lang" in self._ui_config) and (self._ui_config["lang"] == "ger"):
            set_lang_ger()

        self._eval_messages()
        self._set_std_message(all_messages[STD_MSG])

        self._activate_close_button = False
        if ("activate_close_button" in self._ui_config) and (self._ui_config["activate_close_button"] == True):
            self._activate_close_button = True

        return self._ui_config["wait_reader_sec"]

    def force_redraw(self):
        self._redraw()
        pygame.display.update()

    def start(self):
        self._display_surface = pygame.display.set_mode((self._x_size, self._y_size))
        self._set_caption_txt(all_messages[CAPTION_DEFAULT])
        self._font = pygame.font.Font('freesansbold.ttf', self._font_size)
        self._func_font = pygame.font.Font('freesansbold.ttf', self._func_font_size)

    def handle_error(self, err_type, err_msg):
        self._logger(err_msg)
        h = self._text
        b = self._background_col

        self._background_col = self._err_map[err_type]
        self.force_redraw()
        pygame.time.wait(175)

        self._text = h
        self._background_col = b
        self._redraw()        

    def handle_play_start(self, event):
        if event.beep:
            self._sound_bell()

        self._text = all_messages[MSG_PLAY_FORMAT_STR].format(song=event.song, num_songs=event.num_songs)
        self._set_caption_txt(event.play_list_name)

    def handle_pause(self):
        self._set_caption_txt(all_messages[CAPTION_DEFAULT])
        self._text = all_messages[STD_MSG]

    def handle_list_end(self):
        self._set_caption_txt(all_messages[CAPTION_DEFAULT])
        self._text = all_messages[STD_MSG]

    def handle_function_event(self, event):
        self._sound_bell()
        if event.kind == consts.FUNC_END:
            self._text = all_messages[MSG_SHUTDOWN]
            self._redraw()
            pygame.time.wait(200)
            pygame.event.post(pygame.event.Event(self.stopped_event))
        elif event.kind == consts.FUNC_PLAYLIST_RESTART:
            self._func_text = all_messages[MSG_PLAYLIST_BEGINING]
        elif event.kind == consts.FUNC_SONG_RESTART:
            self._func_text =  all_messages[MSG_RESTART_SONG]
        elif event.kind == consts.FUNC_SONG_SKIP:
            self._func_text =  all_messages[MSG_SKIP_SONG]
        elif event.kind == consts.FUNC_SONG_PREV:
            self._func_text = all_messages[MSG_NEXT_SONG]
        elif event.kind == consts.FUNC_PERFORMED:
            self._func_text = EMPTY_STR

    def _load_config(self, config_dir):
        try:
            with(open(os.path.join(config_dir, "ui_config"), "r") as f):
                all_data = json.load(f)

            if "shutdown_command" in all_data.keys():
                cmd = all_data["shutdown_command"]
                consts.set_shutdown_command(cmd)
        except:
            print(all_messages[ERR_MSG_LOAD_CONFIG])
            sys.exit(42)
        
        data = all_data["sounds"]
        self._sound_info = data["info_sound"]
        self._sound_warning = data["warning_sound"]
        self._sound_error = data["error_sound"]

        data = all_data["size"]
        self._x_size = data["x_size"]
        self._y_size = data["y_size"]
        self._font_size = data["font_size1"]
        self._func_font_size = data["font_size2"]

        self._ui_config = all_data

    def _eval_messages(self):
        config = self._ui_config

        if "msgs" in config.keys():
            for i in config["msgs"].keys():
                set_message(i, config["msgs"][i])

    def _set_std_message(self, msg):
        self._text = msg

    def _set_caption_txt(self, txt):
        pygame.display.set_caption(f"{txt} - Version {VERSION_STRING}")

    def _redraw(self):
        text = self._font.render(self._text, True, self.black, self._background_col)
        text_rect = text.get_rect()
        text_rect.center = (self._x_size // 2, self._y_size // 2)
        self._display_surface.fill(self._background_col)
        self._display_surface.blit(text, text_rect)

        text = self._func_font.render(self._func_text, True, self.black, self._background_col)
        text_rect = text.get_rect()
        text_rect.center = (self._x_size // 2, self._y_size // 4)
        self._display_surface.blit(text, text_rect)


    def _err_logger(self, msg):
        self._sound_bell()

    def _sound_bell(self):
        init_was_performed = nfcplaylist.mixer_init()

        sound = pygame.mixer.Sound(self._sound_error)
        sound.play()

        if init_was_performed:
            pygame.time.wait(200)
            nfcplaylist.mixer_stop()
