import pygame
import argparse

import ledwall
print = ledwall.print


# Initialize Mixer for sound
pygame.mixer.init()

# settings --------------------

# read settings from settings.py
# use default values if no settings.py exists
try:
    from settings import *
except ImportError:
    pass

if not 'RENDER_MODE' in dir():
    # 'led' = for led wall output
    # 'plain' = for pc/laptop or testing
    RENDER_MODE = 'plain'

if not 'DEFAULT_BRIGHTNESS' in dir():
    DEFAULT_BRIGHTNESS = None


# read settings from command line
parser = argparse.ArgumentParser(prog='Drunk Duel')
parser.add_argument('--rendermode', default=None, help='possible modes: plain, led')
args = parser.parse_args()

if args.rendermode:
    RENDER_MODE = args.rendermode

    if RENDER_MODE not in ['plain', 'led']:
        print('unknown rendermode: %s' % RENDER_MODE)
        exit()

if DEFAULT_BRIGHTNESS is None:
    if RENDER_MODE == 'led':
        DEFAULT_BRIGHTNESS = -4
    else:
        DEFAULT_BRIGHTNESS = 0


BRIGHTNESS = DEFAULT_BRIGHTNESS

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


# global ----------------------

output = ledwall.initScreen(RENDER_MODE)
ledwall.setBrightnessValue(BRIGHTNESS)

clock = pygame.time.Clock()
tick = 0

TILE_WIDTH = 16
TILE_HEIGHT = 16


def switchState(state):
    global currentScreen
    if state == 'init':
        currentScreen = initScreen
    elif state == 'title':
        currentScreen = titleScreen
    elif state == 'game':
        currentScreen = gameScreen

    ledwall.cls()


def spawnBullet(x, y, xdir):
    bullet = Bullet(x, y)
    bullet.xdir = xdir

    gameScreen.addObject(bullet)

def removeBullet(bullet):
    gameScreen.removeObject(bullet)


lastPlayedFootstep = 0
def playFootstepSound():
    global lastPlayedFootstep
    if tick != lastPlayedFootstep:
        SFX_FOOTSTEP.play()
        lastPlayedFootstep = tick


# sprites and objects ---------

class Sprite:
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
            phase = ((tick - self.startTime) // self.speed) % len(self.animations[0])
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
            self.startTime = tick

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


class Object:
    def __init__(self, xpos, ypos, sprite):
        self.xpos = xpos
        self.ypos = ypos
        self.sprite = sprite

    def draw(self, output):
        self.sprite.draw(output, self.xpos, self.ypos)


class Bullet(Object):
    def __init__(self, xpos, ypos):
        super().__init__(xpos, ypos, BULLET_SPRITE)

        self.xdir = 0
        self.speed = 4

    def update(self):
        self.xpos += self.xdir * self.speed

        if self.xpos < -TILE_WIDTH or self.xpos > ledwall.SCR_W:
            removeBullet(self)


class Player(Object):
    def __init__(self, xpos, ypos, sprite):
        super().__init__(xpos, ypos, sprite)

        self.xdir = 0
        self.ydir = 0
        self.speed = 1.5

        self.facedir = DIR_DOWN

        self.score = 0
        self.ammo = 4
        self.showGun = False

    def moveLeft(self):
        self.xdir = -1
        self.ydir = 0
        self.facedir = DIR_LEFT

    def moveRight(self):
        self.xdir = 1
        self.ydir = 0
        self.facedir = DIR_RIGHT

    def moveUp(self):
        self.xdir = 0
        self.ydir = -1
        self.facedir = DIR_UP

    def moveDown(self):
        self.xdir = 0
        self.ydir = 1
        self.facedir = DIR_DOWN

    def stopLeft(self):
        if self.xdir < 0:
            self.xdir = 0

    def stopRight(self):
        if self.xdir > 0:
            self.xdir = 0

    def stopUp(self):
        if self.ydir < 0:
            self.ydir = 0

    def stopDown(self):
        if self.ydir > 0:
            self.ydir = 0

    def shoot(self):
        self.showGun = True
        self.ammo -= 1

        if self.xpos < 128:
            bulletxdir = 1
            self.facedir = DIR_RIGHT
        else:
            bulletxdir = -1
            self.facedir = DIR_LEFT

        spawnBullet(self.xpos, self.ypos, bulletxdir)
        SFX_GUNSHOT.play(loops=0)

    def stopShooting(self):
        self.showGun = False

    def update(self):
        new_xpos = self.xpos# + self.xdir * self.speed
        new_ypos = self.ypos# + self.ydir * self.speed

        new_xdir = self.xdir
        new_ydir = self.ydir

        tempspeed = self.speed

        # collision with level border:
        if new_xpos < 0:
            new_xpos = 0
            new_xdir = 0

        if new_xpos > (level.getWidth() -1) * TILE_WIDTH:
            new_xpos = (level.getWidth() -1) * TILE_WIDTH
            new_xdir = 0

        if new_ypos < 0:
            new_ypos = 0
            new_ydir = 0

        if new_ypos > (level.getHeight() -1) * TILE_HEIGHT:
            new_ypos = (level.getHeight() -1) * TILE_HEIGHT
            new_ydir = 0

        # collision with tiles:
        x1 = new_xpos // TILE_WIDTH
        y1 = new_ypos // TILE_HEIGHT
        x2 = (new_xpos + TILE_WIDTH -1) // TILE_WIDTH
        y2 = (new_ypos + TILE_HEIGHT -1) // TILE_HEIGHT

        # tiles for coll checK:
        #
        # t1 | t2
        # ---+---
        # t3 | t4

        t1 = level.getTile(x1, y1)
        t2 = level.getTile(x2, y1)
        t3 = level.getTile(x1, y2)
        t4 = level.getTile(x2, y2)

        t1blocked = t1 != ' '
        t2blocked = t2 != ' '
        t3blocked = t3 != ' '
        t4blocked = t4 != ' '

        if new_xdir < 0:   # going left
            if t1blocked and t3blocked:
                new_xdir = 0
            elif t1blocked and not t3blocked:
                new_xdir = 0
                new_ydir = 1
                tempspeed = 1
            elif not t1blocked and t3blocked:
                new_xdir = 0
                new_ydir = -1
                tempspeed = 1

        elif new_xdir > 0: # going right
            if t2blocked and t4blocked:
                new_xdir = 0
            elif t2blocked and not t4blocked:
                new_xdir = 0
                new_ydir = 1
                tempspeed = 1
            elif not t2blocked and t4blocked:
                new_xdir = 0
                new_ydir = -1
                tempspeed = 1

        elif new_ydir < 0: # going up
            if t1blocked and t2blocked:
                new_ydir = 0
            elif t1blocked and not t2blocked:
                new_ydir = 0
                new_xdir = 1
                tempspeed = 1
            elif not t1blocked and t2blocked:
                new_ydir = 0
                new_xdir = -1
                tempspeed = 1

        elif new_ydir > 0: # going down
            if t3blocked and t4blocked:
                new_ydir = 0
            elif t3blocked and not t4blocked:
                new_ydir = 0
                new_xdir = 1
                tempspeed = 1
            elif not t3blocked and t4blocked:
                new_ydir = 0
                new_xdir = -1
                tempspeed = 1

        # calculate new position
        new_xpos += new_xdir * tempspeed
        new_ypos += new_ydir * tempspeed

        # apply changed position
        self.xpos = new_xpos
        self.ypos = new_ypos

        # show animation and play footstep sound
        spriteAnim = self.facedir + (4 if self.showGun else 0)
        self.sprite.select(spriteAnim)

        if self.xdir == 0 and self.ydir == 0:
            self.sprite.stop()
        else:
            self.sprite.start()

            if tick % 8 == 0:
                playFootstepSound()


# screens ---------------------

class Screen:
    def draw(self):
        pass

    def event(self, e):
        pass

    def update(self):
        pass


class InitScreen(Screen):
    def draw(self):
        pass

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            switchState('title')


class TitleScreen(Screen):
    def draw(self):
        ledwall.centerText('DRUNK', y=2, color=(0, 255, 0), fontsize=3, align=False)
        ledwall.centerText('DUEL', y=3, color=(0, 255, 0), fontsize=3, align=False)

        ledwall.centerText('BODENSEE', y=15, color=(255, 255, 255), align=False)
        ledwall.centerText('GAMEJAM', align=False)
        ledwall.centerText('2025', align=False)

        if tick % 48 < 24:
            ledwall.centerText('PRESS BUTTON', y=25, color=(255, 255, 0), align=False)

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            switchState('game')


class GameScreen(Screen):
    def __init__(self):
        super().__init__()

        self.players = []
        self.objects = []

        player1 = Player(2 * TILE_WIDTH, 2 * TILE_HEIGHT, PLAYER_1_SPRITE)
        player2 = Player(13 * TILE_WIDTH, 13 * TILE_HEIGHT, PLAYER_2_SPRITE)

        self.players.append(player1)
        self.players.append(player2)

    def draw(self):
        level.draw(output)

        for player in self.players:
            player.draw(output)

        for obj in self.objects:
            obj.draw(output)

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            for i, keys in enumerate([PLAYER_1_KEYS, PLAYER_2_KEYS]):
                if e.key == keys[DIR_LEFT]:
                    self.players[i].moveLeft()
                elif e.key == keys[DIR_RIGHT]:
                    self.players[i].moveRight()
                elif e.key == keys[DIR_UP]:
                    self.players[i].moveUp()
                elif e.key == keys[DIR_DOWN]:
                    self.players[i].moveDown()

                elif e.key == keys[FIRE]:
                    self.players[i].shoot()

        elif e.type == pygame.KEYUP:
            for i, keys in enumerate([PLAYER_1_KEYS, PLAYER_2_KEYS]):
                if e.key == keys[DIR_LEFT]:
                    self.players[i].stopLeft()
                elif e.key == keys[DIR_RIGHT]:
                    self.players[i].stopRight()
                elif e.key == keys[DIR_UP]:
                    self.players[i].stopUp()
                elif e.key == keys[DIR_DOWN]:
                    self.players[i].stopDown()

                elif e.key == keys[FIRE]:
                    self.players[i].stopShooting()

    def update(self):
        for player in self.players:
            player.update()

        for obj in self.objects:
            obj.update()

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        self.objects.remove(obj)


# init ------------------------

print('welcome to drunk duel')
print('---------------------')
print()
print('rendermode: %s' % RENDER_MODE)
print()

pygame.joystick.init()
numJoysticks = pygame.joystick.get_count()

joysticks = []

if numJoysticks == 0:
    print('no joysticks found')
else:
    print('joysticks found:')

    for i in range(numJoysticks):
        joystick = pygame.joystick.Joystick(i)
        joysticks.append(joystick)

        print('-', joystick.get_name())

print('\n')
print('loading gfx...')

TILES = {'Y': Sprite('gfx/desert3.png'),
         '|': createAnimatedSprite('gfx/water1.png'),
         '#': Sprite('gfx/fence1.png'),
         'o': Sprite('gfx/ston1.png'),
         ' ': None,
         }

PLAYER_1_SPRITE = createAnimatedSprite('gfx/player1.png')
PLAYER_2_SPRITE = createAnimatedSprite('gfx/player2.png')

BULLET_SPRITE = Sprite('gfx/bullet.png')

print('loading sfx...')
SFX_GUNSHOT = pygame.mixer.Sound("sfx/Gunshot.wav")
SFX_FOOTSTEP = pygame.mixer.Sound("sfx/Footstep.wav")

print('\n\n')

print('keyboard:')
print('---------')
print('f1   less brightness')
print('f2   more brightness')
print()

if RENDER_MODE != 'led':
    print('f11  toggle fullscreen')

print('\n\n')

if numJoysticks == 0:
    print('press space to continue')
else:
    print('press space or button')


# level -----------------------

mapdata = ['       ||       ',
           '       ||   Y   ',
           '    Y  ||     o ',
           '       ||       ',
           '       || Y     ',
           '   o   ||       ',
           '      Y||  o    ',
           '       ||    Y  ',
           '  Y    ||       ',
           '   o   ||       ',
           '       ||       ',
           '       ||     o ',
           '     Y ||       ',
           '  o    ||  Y    ',
           '       ||       ',
           '#######||#######',
           ]

class Level:
    def __init__(self, mapdata, tiles):
        self.mapdata = mapdata
        self.tiles = tiles

        self.width = len(self.mapdata[0])
        self.height = len(self.mapdata)

    def setTile(self, x, y, tile):
        self.mapdata[y] = self.mapdata[y][:x] + tile + self.mapdata[y][x+1:]

    def getTile(self, x, y):
        return self.mapdata[int(y)][int(x)]

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def draw(self, output):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.getTile(x, y)
                if tile in self.tiles and self.tiles[tile] is not None:
                    self.tiles[tile].draw(output, x * TILE_WIDTH, y * TILE_HEIGHT)

level = Level(mapdata, TILES)

# animate water
TILES['|'].speed = 12
TILES['|'].start()


# main loop -------------------

initScreen = InitScreen()
titleScreen = TitleScreen()
gameScreen = GameScreen()

currentScreen = initScreen

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
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_F1:
            BRIGHTNESS -= 1
            ledwall.setBrightnessValue(BRIGHTNESS)
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_F2:
            BRIGHTNESS += 1
            if BRIGHTNESS > 0:
                BRIGHTNESS = 0
            ledwall.setBrightnessValue(BRIGHTNESS)
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        else:
            currentScreen.event(e)

    # updates
    currentScreen.update()

    # tick
    clock.tick(60)
    tick += 1

    if currentScreen != initScreen:
        if tick >= 60 * 4:
            ledwall.cls()

