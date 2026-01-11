#! /usr/bin/env python3


import sys
import os
import time
import pathlib
from pygame import mixer
import pygame
import cardy
import playlist
import nfcplaylist_ui
#import nfcplaylist_cli
import consts
import uidfactory
import acr122u
import mixman

MAINTENANCE_INDICATOR = "maintenance"

STATE_IDLE = 0
STATE_PLAYING = 1

NO_SONG = -1

class NfcPlayer:
    def __init__(self, ui, event_insert, event_remove, event_music_end, event_function, event_playing, event_pause, event_list_end, ui_stopped, err_generic, event_first_card):
        self.insert = event_insert
        self.remove = event_remove
        self.play_end = event_music_end
        self.function_event = event_function
        self.play_start_event = event_playing
        self.event_pause = event_pause
        self.event_list_end = event_list_end
        self.event_ui_stopped = ui_stopped
        self.state = STATE_IDLE
        self.playing_id = NO_SONG
        self.perform_function = None
        self._end_program = False
        self.event_err_gen = err_generic
        self.event_first_card = event_first_card
        self.ui = ui
        self.activate_close_button = ui.activate_close_button
        self._config_dir = ""
        self._mix_man = mixman.MixerManager(False)

        self.card_id_rewind = ui.card_ids["rewind"]
        self.card_id_restart = ui.card_ids["restart"]
        self.card_id_end = ui.card_ids["end"]
        self.card_id_skip = ui.card_ids["skip"]
        self.card_id_prev = ui.card_ids["prev"]
        self.titles = {}
        self._first_handler = lambda x: None

    def get_playlists(self, config_dir):
        all_files = []
        for file in os.listdir(config_dir):
            if file.endswith(".json"):
                all_files.append(os.path.join(config_dir, file))

        return list(map(playlist.PlayList.from_json, all_files))

    def assign_playlists(self, pls):
        self.titles = {}
        for i in pls:
            self.titles[i.card_id] = i

    def reload_playlists(self):
        try:
            titles_raw = self.get_playlists(self._config_dir)
        except:
            return

        self.assign_playlists(titles_raw)

    def load_playlists(self, config_dir):
        try:
            titles_raw = self.get_playlists(config_dir)
        except:
            print("Unable to load playlists")
            sys.exit(42)

        self.assign_playlists(titles_raw)
        self._config_dir = config_dir

    @staticmethod
    def prep_function_execution(f, ctx):
        def prepper(x):
            f(x)
            return ctx

        return prepper

    @property
    def first_handler(self):
        return self._first_handler

    @first_handler.setter
    def first_handler(self, val):
        self._first_handler = val

    @property
    def end_program(self):
        return self._end_program

    def handle_insert_event(self, event):
        if self.state != STATE_IDLE:
            return
        
        self.reload_playlists()

        if event.card_id == self.card_id_rewind:
            self.perform_function = NfcPlayer.prep_function_execution(lambda x: x.reset(), consts.FUNC_PLAYLIST_RESTART)
            pygame.event.post(pygame.event.Event(self.function_event, kind=consts.FUNC_PLAYLIST_RESTART, ctx=None))
        elif event.card_id == self.card_id_restart:
            self.perform_function = NfcPlayer.prep_function_execution(lambda x: x.reset_play_time(), consts.FUNC_SONG_RESTART)
            pygame.event.post(pygame.event.Event(self.function_event, kind=consts.FUNC_SONG_RESTART, ctx=None))
        elif event.card_id == self.card_id_skip:
            self.perform_function = NfcPlayer.prep_function_execution(lambda x: x.skip_song(), consts.FUNC_SONG_SKIP)
            pygame.event.post(pygame.event.Event(self.function_event, kind=consts.FUNC_SONG_SKIP, ctx=None))
        elif event.card_id == self.card_id_prev:
            self.perform_function = NfcPlayer.prep_function_execution(lambda x: x.prev_song(), consts.FUNC_SONG_PREV)
            pygame.event.post(pygame.event.Event(self.function_event, kind=consts.FUNC_SONG_PREV, ctx=None))
        elif event.card_id == self.card_id_end:
            pygame.event.post(pygame.event.Event(self.function_event, kind=consts.FUNC_END, ctx=None))
        else:
            if not event.card_id in self.titles.keys():
                return

            pl = self.titles[event.card_id]
            restore_play_time = pl.get_play_time()
            restore_title = pl.get_current_song_num()

            try:
                if self.perform_function != None:
                    context = self.perform_function(self.titles[event.card_id])
                    pygame.event.post(pygame.event.Event(self.function_event, kind=consts.FUNC_PERFORMED, ctx=context))
                    self.perform_function = None

                if not pathlib.Path(pl.current_song()).exists():
                    raise Exception("File does not exist")

                self._mix_man.init()
                mixer.music.load(pl.current_song())
                start_pos = pl.get_play_time()

                mixer.music.play(start = start_pos)
                self.playing_id = event.card_id
                self.state = STATE_PLAYING
                pygame.event.post(pygame.event.Event(self.play_start_event, play_list_name=pl.play_list_name(), song=pl.get_current_song_num()+1, num_songs=pl.num_songs(), beep=event.beep))
            except Exception as e:
                pygame.event.post(pygame.event.Event(self.event_err_gen, err_type=consts.ERR_TYPE_FILE, err_msg=str(e)))
                pl.set_play_time(restore_play_time)
                pl.set_current_song_num(restore_title)

    def handle_remove_event(self, event):
        if self.state != STATE_PLAYING:
            return

        if event.card_id != self.playing_id:
            return
        
        self.titles[self.playing_id].increase_play_time(mixer.music.get_pos() / 1000.0)
        self.playing_id = NO_SONG
        self.state = STATE_IDLE
        mixer.music.stop()
        self._mix_man.stop(None)
        pygame.event.post(pygame.event.Event(self.event_pause))

    def handle_song_end(self):
        if self.state != STATE_PLAYING:
            return

        playlist_end = self.titles[self.playing_id].next_song()
        if playlist_end:
            self.titles[self.playing_id].reset()
            self.playing_id = NO_SONG
            self.state = STATE_IDLE
            self._mix_man.stop(None)
            pygame.event.post(pygame.event.Event(self.event_list_end))
            return
        
        h = self.playing_id
        self.playing_id = NO_SONG
        self.state = STATE_IDLE
        pygame.event.post(pygame.event.Event(self.insert, card_id=h, beep=False))

    def work_event_queue(self):
        event = pygame.event.wait()
        if event.type == self.insert:
            self.handle_insert_event(event)
        elif event.type == self.remove:
            self.handle_remove_event(event)
        elif event.type == self.play_end:
            self.handle_song_end()
        elif event.type == self.event_err_gen:
            self.ui.handle_error(event.err_type, event.err_msg)
        elif event.type == self.function_event:
            self.ui.handle_function_event(event)
        elif event.type == self.play_start_event:
            self.ui.handle_play_start(event)
        elif event.type == self.event_pause:
            self.ui.handle_pause()
        elif event.type == self.event_list_end:
            self.ui.handle_list_end()
        elif event.type == self.event_ui_stopped:
            self._end_program = True
        elif event.type == self.event_first_card:
            self.first_handler(event.card_obj)
        elif event.type == pygame.QUIT:
            if self.activate_close_button:
                self._end_program = True


def init_reader(wait_time):
    sys.stdout.write("Waiting for reader ... ")
    sys.stdout.flush()

    time.sleep(wait_time)

    print("done")


def printing_logger(msg):
    print(msg)


def run_player(config_dir):
    # Last parameter is buffer size. Maybe increase it further if sound starts to lag
    mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    mixman.MixerManager.stop_if_initialized()

    event_insert = pygame.event.custom_type()
    event_remove = pygame.event.custom_type()
    event_music_end = pygame.event.custom_type()
    event_function = pygame.event.custom_type()
    event_playing = pygame.event.custom_type()
    event_pause = pygame.event.custom_type()
    event_list_end = pygame.event.custom_type()
    event_ui_stopped = pygame.event.custom_type()
    event_err_generic = pygame.event.custom_type()
    event_first_card = pygame.event.custom_type()
    pygame.mixer.music.set_endevent(event_music_end)

    ui = nfcplaylist_ui.NfcPlaylistUI(event_ui_stopped)
    #ui = nfcplaylist_cli.NfcPlaylistUI(event_ui_stopped)
    #ui.logger = printing_logger
    reader_wait_time = ui.init(config_dir)

    player = NfcPlayer(ui, event_insert, event_remove, event_music_end, event_function, event_playing, event_pause, event_list_end, event_ui_stopped, event_err_generic, event_first_card)
    player.load_playlists(config_dir)
    player.first_handler = lambda x: acr122u.buzzer_off(x) if (str(x).find("ACS ACR122U") != -1) else None

    card_manager = cardy.CardManager(consts.ALL_ATRS, uidfactory.UidReaderRepo(), event_insert, event_remove, event_err_generic, event_first_card)
    card_manager.start()

    init_reader(reader_wait_time)

    try:
        # empty event queue, i.e. initial card errors
        _ = pygame.event.get()
        ui.start()

        while not player.end_program:
            player.work_event_queue()
            ui.force_redraw()
    except KeyboardInterrupt:
        pass
    except:
        # If any exception occurs shutdown machine and let the user restart
        # it
        pass
    finally:
        card_manager.destroy()
        pygame.quit()


def maintenance_requested(config_dir):
    p = pathlib.Path(config_dir) / MAINTENANCE_INDICATOR
    res = p.exists()

    #ignore errors
    try:
        if res:
            p.unlink()
    except:
        pass

    return res


def main():
    os.system(consts.get_clear_command())

    config_dir = "./"
    if len(sys.argv) > 1:
        config_dir = sys.argv[1]

    run_player(config_dir)

    if not maintenance_requested(config_dir):
        os.system(consts.get_shutdown_command())


if __name__ == "__main__":
    main()