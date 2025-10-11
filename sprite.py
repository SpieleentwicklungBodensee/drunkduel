import pygame
import game_state

# Override print function
import ledwall
print = ledwall.print



class Sprite:
    """Basic sprite class for displaying images."""

    def __init__(self, filenameOrSurface):
        if type(filenameOrSurface) is str:
            self.surface = pygame.image.load(filenameOrSurface)
        else:
            self.surface = filenameOrSurface

    def draw(self, output, x, y):
        output.blit(self.surface, (x, y))

class AnimSprite:
    def __init__(self, animations=None):
        # 2d array of animations with phases
        # e.g.:
        #
        # [[walk left 1, walk left 2],
        #  [walk right 1, walk right 2],
        #  ...]
        #
        self.animations = animations

        self.anim = 0
        self.speed = 6
        self.startTime = 0
        self.lastPhase = 0

        self.running = False

    def draw(self, output, x, y):
        if self.running:
            phase = ((game_state.tick - self.startTime) // self.speed) % len(self.animations[0])
            self.lastPhase = phase
        else:
            phase = self.lastPhase

        sprite = self.animations[self.anim][phase]
        sprite.draw(output, x, y)

    def select(self, animation):
        self.anim = animation

    def start(self, reset=False):
        self.running = True
        if reset:
            self.startTime = game_state.tick

    def stop(self, reset=True):
        self.running = False
        if reset:
            self.lastPhase = 0

def createAnimatedSprite(filename, width=16, height=16):
    animations = []
    sprite = pygame.image.load(filename)

    for anim in range(sprite.get_height() // height):
        phases = []
        for phase in range(sprite.get_width() // width):
            blitx = 0 - phase * width
            blity = 0 - anim * height

            slice_ = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            slice_.blit(sprite, (blitx, blity))

            phases.append(Sprite(slice_))

        animations.append(phases)

    return AnimSprite(animations)
