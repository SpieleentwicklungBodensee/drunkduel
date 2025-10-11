import pygame
from base import Screen
from game_state import switchState

# Override print function
import ledwall
print = ledwall.print


class InitScreen(Screen):
    def draw(self):
        pass

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            switchState('title')