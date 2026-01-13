import configurator
import consts


class NfcPlaylistUI(configurator.UiBase):
    def __init__(self, event_ui_stopped):
        super().__init__(event_ui_stopped)

    def init(self, config_dir):
        self._load_config(config_dir)

        return self._ui_config["wait_reader_sec"]

    def force_redraw(self):
        pass

    def start(self):
        print(f"Program start. Version {consts.VERSION_STRING}")

    def handle_error(self, err_type, err_msg):
        self._logger(err_msg)
        print(f"Error type {err_type}: {err_msg}")

    def handle_play_start(self, event):
        if event.beep:
            self._sound_bell()
        print(f"Playlist: '{event.play_list_name}' {"Chapter {song} of {num_songs}".format(song=event.song, num_songs=event.num_songs)}")

    def handle_pause(self):
        print("Pause")

    def handle_list_end(self):
        print("Playlist has ended")

    def handle_all_func_events(self, event):
        if event.kind == consts.FUNC_END:
            print("Good bye")
        elif event.kind == consts.FUNC_PLAYLIST_RESTART:
            print("Restart whole playlist")
        elif event.kind == consts.FUNC_SONG_RESTART:
            print("Restart chapter")
        elif event.kind == consts.FUNC_SONG_SKIP:
            print("Next chapter")
        elif event.kind == consts.FUNC_SONG_PREV:
            print("Previous chapter")
        elif event.kind == consts.FUNC_PERFORMED:
            print("Done")
        
        return True
