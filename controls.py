import pygame

DIR_LEFT = 3
DIR_RIGHT = 2
DIR_UP = 1
DIR_DOWN = 0
FIRE = 5


PLAYER_2_KEYS = {DIR_LEFT: pygame.K_LEFT,
                 DIR_RIGHT: pygame.K_RIGHT,
                 DIR_UP: pygame.K_UP,
                 DIR_DOWN: pygame.K_DOWN,
                 FIRE: pygame.K_RCTRL,
                 }

PLAYER_1_KEYS = {DIR_LEFT: pygame.K_a,
                 DIR_RIGHT: pygame.K_d,
                 DIR_UP: pygame.K_w,
                 DIR_DOWN: pygame.K_s,
                 FIRE: pygame.K_TAB,
                 }
