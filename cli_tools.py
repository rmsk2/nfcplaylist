import pygame
import uidfactory
import collections
import cardy
import consts


def wait_for_card(event_insert):
    card_id = None

    while card_id == None:
        event = pygame.event.wait()
        if event.type == event_insert:
            card_id = event.card_id
    
    return card_id 


# Ok let's massively overengineer this ;-)
class Deferrer:
    def __init__(self):
        self._deferred = collections.deque()

    def defer(self, f):
        self._deferred.appendleft(f)

    def unwind(self):
        for f in self._deferred:
            f()


def main(payload_func):
    try:
        deferrer = Deferrer()

        pygame.init()
        deferrer.defer(pygame.quit)
        event_insert = pygame.event.custom_type()
        event_remove = pygame.event.custom_type()
        event_err_generic = pygame.event.custom_type()
        event_first_card = pygame.event.custom_type()

        card_manager = cardy.CardManager(consts.ALL_ATRS, uidfactory.UidReaderRepo(), event_insert, event_remove, event_err_generic, event_first_card)
        card_manager.start()
        deferrer.defer(card_manager.destroy)

        payload_func(event_insert)        
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)
    finally:
        deferrer.unwind()