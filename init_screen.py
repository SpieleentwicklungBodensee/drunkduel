import pygame
import ledwall
from base import Screen
from game_state import switchState

from level_loader import get_level_loader

# Override print function
print = ledwall.print



class InitScreen(Screen):
    def __init__(self):
        super().__init__()
        ledwall.autoClearPrints = False

    def draw(self):
        pass

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            switchState('title')
            ledwall.autoClearPrints = True