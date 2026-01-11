import os
import json
import sys
import mixman
import pygame
import consts

class UiBase:
    def __init__(self, event_ui_stopped):
        self.stopped_event = event_ui_stopped
        self._activate_close_button = False
        self._ui_config = {}
        self._logger = self._err_logger

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

    def handle_function_event(self, event):
        self._sound_bell()
        do_stop = self.handle_all_func_events(event)
        if (event.kind == consts.FUNC_END) and do_stop:
            self._signal_ui_stopped()
    
    # Override this method. Return a bool. If consts.FUNC_END is handled this bool
    # determines if the program stops (True) or not (False)
    def handle_all_func_events(event):
        pass

    def _signal_ui_stopped(self):
        pygame.event.post(pygame.event.Event(self.stopped_event))

    def _load_config(self, config_dir):
        try:
            with(open(os.path.join(config_dir, "ui_config"), "r") as f):
                all_data = json.load(f)
        except:
            print("Unable to load configuration")
            sys.exit(42)
        
        if "shutdown_command" in all_data.keys():
            cmd = all_data["shutdown_command"]
            consts.set_shutdown_command(cmd)

        data = all_data["sounds"]
        self._sound_info = data["info_sound"]
        self._sound_warning = data["warning_sound"]
        self._sound_error = data["error_sound"]

        self._ui_config = all_data

        self._activate_close_button = False
        if ("activate_close_button" in self._ui_config) and (self._ui_config["activate_close_button"] == True):
            self._activate_close_button = True

    def _err_logger(self, msg):
        print(f"Error logger: {msg}")
        self._sound_bell()

    def _sound_bell(self):
        mix_man = mixman.MixerManager()
        pygame.mixer.Sound(self._sound_error).play()
        mix_man.stop(lambda: pygame.time.wait(200))

