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

JOYSTICKS = []


JOYSTATES = [{DIR_LEFT: False,
              DIR_RIGHT: False,
              DIR_UP: False,
              DIR_DOWN: False,
              FIRE: False,
              },

             {DIR_LEFT: False,
              DIR_RIGHT: False,
              DIR_UP: False,
              DIR_DOWN: False,
              FIRE: False,
              },
              ]

def translateDirection(key, mapping):
    idx = list(mapping.values()).index(key)
    direction = list(mapping.keys())[idx]
    return direction



def _moveDir(player, playerid, direction):
    if direction == DIR_LEFT:
        player.moveLeft()
    elif direction == DIR_RIGHT:
        player.moveRight()
    elif direction == DIR_UP:
        player.moveUp()
    elif direction == DIR_DOWN:
        player.moveDown()
    elif direction == FIRE:
        player.shoot(playerid)

def _stopDir(player, playerid, direction):
    if direction == DIR_LEFT:
        player.stopLeft()
    elif direction == DIR_RIGHT:
        player.stopRight()
    elif direction == DIR_UP:
        player.stopUp()
    elif direction == DIR_DOWN:
        player.stopDown()
    elif direction == FIRE:
        player.stopShooting()

def handleJoyEvent(e, players):
    joyid = e.instance_id
    player = players[joyid]
    mapping = (PLAYER_1_KEYS, PLAYER_2_KEYS)[joyid]
    action = ''

    if e.type == pygame.JOYAXISMOTION:
        if e.axis == 0: # x axis
            if e.value < 0:
                JOYSTATES[joyid][DIR_LEFT] = True
                action = 'moveleft'
            elif e.value > 0:
                JOYSTATES[joyid][DIR_RIGHT] = True
                action = 'moveright'
            else:
                if JOYSTATES[joyid][DIR_LEFT]:
                    JOYSTATES[joyid][DIR_LEFT] = False
                    action = 'stopleft'
                if JOYSTATES[joyid][DIR_RIGHT]:
                    JOYSTATES[joyid][DIR_RIGHT] = False
                    action = 'stopright'
        elif e.axis == 1: # y axis
            if e.value < 0:
                JOYSTATES[joyid][DIR_UP] = True
                action = 'moveup'
            elif e.value > 0:
                JOYSTATES[joyid][DIR_DOWN] = True
                action = 'movedown'
            else:
                if JOYSTATES[joyid][DIR_UP]:
                    JOYSTATES[joyid][DIR_UP] = False
                    action = 'stopup'
                if JOYSTATES[joyid][DIR_DOWN]:
                    JOYSTATES[joyid][DIR_DOWN] = False
                    action = 'stopdown'

        if action == 'moveleft':
            actualDir = translateDirection((pygame.K_LEFT, pygame.K_a)[1-joyid], mapping)
            _moveDir(player, joyid, actualDir)
        elif action == 'moveright':
            actualDir = translateDirection((pygame.K_RIGHT, pygame.K_d)[1-joyid], mapping)
            _moveDir(player, joyid, actualDir)
        elif action == 'moveup':
            actualDir = translateDirection((pygame.K_UP, pygame.K_w)[1-joyid], mapping)
            _moveDir(player, joyid, actualDir)
        elif action == 'movedown':
            actualDir = translateDirection((pygame.K_DOWN, pygame.K_s)[1-joyid], mapping)
            _moveDir(player, joyid, actualDir)

        if action == 'stopleft':
            actualDir = translateDirection((pygame.K_LEFT, pygame.K_a)[1-joyid], mapping)
            _stopDir(player, joyid, actualDir)
        elif action == 'stopright':
            actualDir = translateDirection((pygame.K_RIGHT, pygame.K_d)[1-joyid], mapping)
            _stopDir(player, joyid, actualDir)
        elif action == 'stopup':
            actualDir = translateDirection((pygame.K_UP, pygame.K_w)[1-joyid], mapping)
            _stopDir(player, joyid, actualDir)
        elif action == 'stopdown':
            actualDir = translateDirection((pygame.K_DOWN, pygame.K_s)[1-joyid], mapping)
            _stopDir(player, joyid, actualDir)

    elif e.type == pygame.JOYBUTTONDOWN:
        actualDir = translateDirection((pygame.K_TAB, pygame.K_RCTRL)[joyid], mapping)
        _moveDir(player, joyid, actualDir)

    elif e.type == pygame.JOYBUTTONUP:
        actualDir = translateDirection((pygame.K_TAB, pygame.K_RCTRL)[joyid], mapping)
        _stopDir(player, joyid, actualDir)

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