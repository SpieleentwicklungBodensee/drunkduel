import pygame

import ledwall
print = ledwall.print

# read settings from settings.py
# use default values if no settings.py exists
try:
    from settings import *
except ImportError:
    pass

if not 'RENDER_MODE' in dir():
    # 'led' = for led wall output
    # 'plain' = for pc/laptop or testing
    # 'sim' = led simulation for uli (deprecated)
    # 'arcade' = for toolbox arcade cabinet
    # 'square' = for square displays
    RENDER_MODE = 'plain'

if not 'DEFAULT_BRIGHTNESS' in dir():
    if RENDER_MODE == 'led':
        BRIGHTNESS = -4
    else:
        BRIGHTNESS = 0


# global ----------------------

output = ledwall.initScreen(RENDER_MODE)
ledwall.setBrightnessValue(BRIGHTNESS)

clock = pygame.time.Clock()
tick = 0


# screens ---------------------

class Screen:
    def draw(self):
        pass

    def event(self, e):
        pass


class TitleScreen(Screen):
    def draw(self):
        ledwall.centerText('DRUNK', y=2, color=(0, 255, 0), fontsize=3, align=False)
        ledwall.centerText('DUEL', y=3, color=(0, 255, 0), fontsize=3, align=False)

        ledwall.centerText('BODENSEE', y=15, color=(255, 255, 255), align=False)
        ledwall.centerText('GAMEJAM', align=False)
        ledwall.centerText('2025', align=False)

    def event(self, e):
        pass

class GameScreen(Screen):
    def draw(self):
        pass

    def event(self, e):
        pass


# main loop -------------------

titleScreen = TitleScreen()
gameScreen = GameScreen()

currentScreen = titleScreen

running = True

while running:
    # draw
    output.fill((0, 0, 0))
    currentScreen.draw()
    ledwall.compose(do_cls=False)

    # events
    events = pygame.event.get()

    for e in events:
        if e.type==pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False
        else:
            currentScreen.event(e)

    # tick
    clock.tick(60)
    tick += 1

    if tick >= 60 * 4:
        ledwall.cls()

