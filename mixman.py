import pygame
from pygame import mixer

class MixerManager:
    def __init__(self, do_init = True):
        self._was_initialized_by_me = None

        if do_init:
            self._force_init()

    def init(self):
        if self._was_initialized_by_me != True:
            self._force_init()

    def _force_init(self):
        if pygame.mixer.get_init() == None:
            mixer.init()
            self._was_initialized_by_me = True
            #print("init")
        else:
            self._was_initialized_by_me = False

    @staticmethod
    def stop_if_initialized():
        if pygame.mixer.get_init() != None:
            mixer.quit()
            #print("deinit")

    def stop(self, end_func):
        if self._was_initialized_by_me == True:
            if end_func != None:
                end_func()
            MixerManager.stop_if_initialized()
            self._was_initialized_by_me = False