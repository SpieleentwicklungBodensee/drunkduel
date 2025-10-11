import pygame
import random

DIR_LEFT = 3
DIR_RIGHT = 2
DIR_UP = 1
DIR_DOWN = 0
FIRE = 5


NAMES = {DIR_LEFT: 'links',
         DIR_RIGHT: 'rechts',
         DIR_UP: 'hoch',
         DIR_DOWN: 'runter',
         FIRE: 'feuer',
         }

PLAYER_2_KEYS_ORIGINAL = {DIR_LEFT: pygame.K_LEFT,
                          DIR_RIGHT: pygame.K_RIGHT,
                          DIR_UP: pygame.K_UP,
                          DIR_DOWN: pygame.K_DOWN,
                          FIRE: pygame.K_RCTRL,
                          }

PLAYER_1_KEYS_ORIGINAL = {DIR_LEFT: pygame.K_a,
                          DIR_RIGHT: pygame.K_d,
                          DIR_UP: pygame.K_w,
                          DIR_DOWN: pygame.K_s,
                          FIRE: pygame.K_TAB,
                          }

PLAYER_1_KEYS = PLAYER_1_KEYS_ORIGINAL.copy()
PLAYER_2_KEYS = PLAYER_2_KEYS_ORIGINAL.copy()


def restore(playerid):
    global PLAYER_1_KEYS, PLAYER_2_KEYS

    if playerid == 0:
        PLAYER_1_KEYS = PLAYER_1_KEYS_ORIGINAL.copy()
    elif playerid == 1:
        PLAYER_2_KEYS = PLAYER_2_KEYS_ORIGINAL.copy()

def swapRandomly(keymapping):
    available = list(range(len(keymapping)))
    chosen1 = random.choice(available)

    available.remove(chosen1)
    chosen2 = random.choice(available)

    # swap chosen1 with chosen2
    origKey = list(keymapping.keys())[chosen1]
    replKey = list(keymapping.keys())[chosen2]

    origVal = keymapping[origKey]
    replVal = keymapping[replKey]

    keymapping[origKey] = replVal
    keymapping[replKey] = origVal

    return origKey, replKey

def getSentence(key1, key2):
    return (NAMES[key1], 'ist', NAMES[key2])