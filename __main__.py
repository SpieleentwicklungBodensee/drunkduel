import pygame
import argparse

import ledwall
print = ledwall.print

import controls
import random
import math
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
    elif state == 'gameover':
        currentScreen = gameOverScreen

    ledwall.cls()


def spawnBullet(x, y, xdir, shooter_index):
    bullet = Bullet(x, y)
    bullet.xdir = xdir
    bullet.shooter_index = shooter_index

    gameScreen.addObject(bullet)

def removeBullet(bullet):
    gameScreen.removeObject(bullet)

def spawnWeaponDrop():
    import random
    # Find a random empty spot on the map
    attempts = 0
    while attempts < 100:  # Prevent infinite loop
        x = random.randint(0, level.getWidth() - 1)
        y = random.randint(0, level.getHeight() - 1)

        if level.getTile(x, y) == ' ':  # Empty space
            weapon_drop = WeaponDrop(x * TILE_WIDTH, y * TILE_HEIGHT)
            gameScreen.addObject(weapon_drop)
            break
        attempts += 1

def checkWeaponPickup():
    # Check if players pick up weapon drops
    for weapon_drop in gameScreen.objects[:]:
        if isinstance(weapon_drop, WeaponDrop):
            for player in gameScreen.players:
                # Check collision with player
                if (weapon_drop.xpos < player.xpos + TILE_WIDTH and
                    weapon_drop.xpos + TILE_WIDTH > player.xpos and
                    weapon_drop.ypos < player.ypos + TILE_HEIGHT and
                    weapon_drop.ypos + TILE_HEIGHT > player.ypos):

                    # Player picks up ammo
                    player.ammo = min(player.ammo + weapon_drop.ammo_amount, 10)  # Max 10 ammo

                    # Remove the weapon drop
                    gameScreen.removeObject(weapon_drop)

                    # Play pickup sound (reuse footstep for now)
                    SFX_FOOTSTEP.play()
                    break

def checkCollisions():
    # Check bullet-player collisions
    for bullet in gameScreen.objects[:]:  # Use slice to avoid modification during iteration
        if isinstance(bullet, Bullet):
            for i, player in enumerate(gameScreen.players):
                # Skip collision check with the player who shot the bullet
                if i == bullet.shooter_index:
                    continue

                # Simple bounding box collision detection
                if (bullet.xpos < player.xpos + TILE_WIDTH and
                    bullet.xpos + TILE_WIDTH > player.xpos and
                    bullet.ypos < player.ypos + TILE_HEIGHT and
                    bullet.ypos + TILE_HEIGHT > player.ypos):

                    # Collision detected - increase score for the other player
                    other_player_index = 1 - i
                    gameScreen.players[other_player_index].score += 1

                    # Give shooter some ammo back as reward
                    gameScreen.players[other_player_index].ammo = min(gameScreen.players[other_player_index].ammo + 2, 6)

                    # Remove bullet and play sound effect
                    removeBullet(bullet)
                    SFX_PLAYER_HIT.play()

                    # Reset hit player position
                    if i == 0:  # Player 1 hit
                        player.xpos = 2 * TILE_WIDTH
                        player.ypos = 2 * TILE_HEIGHT
                    else:  # Player 2 hit
                        player.xpos = 13 * TILE_WIDTH
                        player.ypos = 13 * TILE_HEIGHT

                    # Reset ammo for hit player
                    player.ammo = 4

                    # Check for victory condition (first to 5 points wins)
                    if gameScreen.players[other_player_index].score >= 5:
                        gameScreen.winner = other_player_index + 1
                        switchState('gameover')

                    # switch controls
                    keymapping = [controls.PLAYER_1_KEYS, controls.PLAYER_2_KEYS][bullet.shooter_index]
                    orig, repl = controls.swapRandomly(keymapping)

                    ledwall.cls()
                    print('spieler %s:' % bullet.shooter_index)
                    print(controls.getSentence(orig, repl))

                    break


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


class Explosion(Object):
    def __init__(self, xpos, ypos):
        # Create a simple explosion sprite (we'll draw particles)
        explosion_surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), flags=pygame.SRCALPHA)
        super().__init__(xpos, ypos, Sprite(explosion_surface))

        self.particles = []
        self.lifetime = 30  # frames
        self.age = 0

        # Create particles
        import random
        for i in range(8):
            particle = {
                'x': xpos + TILE_WIDTH // 2,
                'y': ypos + TILE_HEIGHT // 2,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': random.randint(15, 25)
            }
            self.particles.append(particle)

    def update(self):
        self.age += 1

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # gravity
            particle['life'] -= 1

            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Remove explosion when done
        if self.age >= self.lifetime or len(self.particles) == 0:
            gameScreen.removeObject(self)

    def draw(self, output):
        # Draw particles as colored pixels
        for particle in self.particles:
            if particle['life'] > 0:
                # Color fades from yellow to red
                life_ratio = particle['life'] / 25.0
                color = (255, int(255 * life_ratio), 0)
                x, y = int(particle['x']), int(particle['y'])
                if 0 <= x < ledwall.SCR_W and 0 <= y < ledwall.SCR_H:
                    pygame.draw.circle(output, color, (x, y), 2)


class WeaponDrop(Object):
    def __init__(self, xpos, ypos):
        super().__init__(xpos, ypos, MUNITION_SPRITE)
        self.ammo_amount = 3  # How much ammo this drop gives
        self.bob_offset = 0   # For floating animation

    def update(self):
        # Floating animation
        self.bob_offset += 0.1
        # The sprite will bob up and down slightly

    def draw(self, output):
        # Draw with slight vertical bobbing animation
        bob_y = self.ypos + math.sin(self.bob_offset) * 2
        self.sprite.draw(output, self.xpos, int(bob_y))


class Bullet(Object):
    def __init__(self, xpos, ypos):
        super().__init__(xpos, ypos, BULLET_SPRITE)

        self.xdir = 0
        self.speed = 4
        self.shooter_index = -1  # Will be set when spawned

    def update(self):
        self.xpos += self.xdir * self.speed

        # Check for collision with tiles
        tile_x = int(self.xpos // TILE_WIDTH)
        tile_y = int(self.ypos // TILE_HEIGHT)

        if 0 <= tile_x < level.getWidth() and 0 <= tile_y < level.getHeight():
            tile = level.getTile(tile_x, tile_y)
            if tile == 'Y':  # Hit a cactus - explode it
                # Create explosion effect
                explosion = Explosion(tile_x * TILE_WIDTH, tile_y * TILE_HEIGHT)
                gameScreen.addObject(explosion)

                # Remove the cactus from the map
                level.setTile(tile_x, tile_y, ' ')

                # Play explosion sound
                SFX_EXPLOSION.play()

                # 30% chance to spawn a weapon drop where the cactus was
                if random.random() < 0.3:
                    weapon_drop = WeaponDrop(tile_x * TILE_WIDTH, tile_y * TILE_HEIGHT)
                    gameScreen.addObject(weapon_drop)

                # Remove the bullet
                removeBullet(self)
                return
            elif tile in ['#', 'o']:  # Hit fence or stone - just bounce/disappear
                # Play ricochet sound
                SFX_RICOCHET.play()

                # Remove the bullet
                removeBullet(self)
                return

        if self.xpos < -TILE_WIDTH or self.xpos > ledwall.SCR_W:
            removeBullet(self)


class Player(Object):
    def __init__(self, xpos, ypos, sprite):
        super().__init__(xpos, ypos, sprite)

        self.xdir = 0
        self.ydir = 0
        self.speed = 1.5

        self.facedir = controls.DIR_DOWN

        self.score = 0
        self.ammo = 4
        self.showGun = False

    def moveLeft(self):
        self.xdir = -1
        self.ydir = 0
        self.facedir = controls.DIR_LEFT

    def moveRight(self):
        self.xdir = 1
        self.ydir = 0
        self.facedir = controls.DIR_RIGHT

    def moveUp(self):
        self.xdir = 0
        self.ydir = -1
        self.facedir = controls.DIR_UP

    def moveDown(self):
        self.xdir = 0
        self.ydir = 1
        self.facedir = controls.DIR_DOWN

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

    def shoot(self, player_index):
        if self.ammo <= 0:
            return  # Can't shoot without ammo

        self.showGun = True
        self.ammo -= 1

        if self.xpos < 128:
            bulletxdir = 1
            self.facedir = controls.DIR_RIGHT
        else:
            bulletxdir = -1
            self.facedir = controls.DIR_LEFT

        spawnBullet(self.xpos, self.ypos, bulletxdir, player_index)
        SFX_GUNSHOT.play(loops=0)

    def stopShooting(self):
        self.showGun = False

    def update(self):
        new_xpos = self.xpos
        new_ypos = self.ypos

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


class GameOverScreen(Screen):
    def draw(self):
        ledwall.centerText('GAME OVER', y=5, color=(255, 0, 0), fontsize=2, align=False)

        if hasattr(gameScreen, 'winner'):
            ledwall.centerText(f'PLAYER {gameScreen.winner}', y=10, color=(0, 255, 0), fontsize=2, align=False)
            ledwall.centerText('WINS!', y=12, color=(0, 255, 0), fontsize=2, align=False)

            ledwall.centerText(f'FINAL SCORE:', y=17, color=(255, 255, 255), align=False)
            ledwall.centerText(f'P1: {gameScreen.players[0].score}  P2: {gameScreen.players[1].score}', y=19, color=(255, 255, 255), align=False)

        if tick % 48 < 24:
            ledwall.centerText('PRESS BUTTON', y=25, color=(255, 255, 0), align=False)
            ledwall.centerText('TO RESTART', y=27, color=(255, 255, 0), align=False)

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            # Reset game state
            gameScreen.players[0].score = 0
            gameScreen.players[1].score = 0
            gameScreen.players[0].ammo = 4
            gameScreen.players[1].ammo = 4
            gameScreen.players[0].xpos = 2 * TILE_WIDTH
            gameScreen.players[0].ypos = 2 * TILE_HEIGHT
            gameScreen.players[1].xpos = 13 * TILE_WIDTH
            gameScreen.players[1].ypos = 13 * TILE_HEIGHT
            gameScreen.objects.clear()  # Remove all bullets and weapon drops
            gameScreen.weapon_drop_timer = 0  # Reset weapon drop timer
            if hasattr(gameScreen, 'winner'):
                delattr(gameScreen, 'winner')
            switchState('game')


class GameScreen(Screen):
    def __init__(self):
        super().__init__()

        self.players = []
        self.objects = []
        self.weapon_drop_timer = 0  # Timer for spawning weapon drops

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

        # Draw highscore display
        ledwall.drawText(f'P1: {self.players[0].score}', x=2, y=2, color=(255, 255, 0))
        ledwall.drawText(f'P2: {self.players[1].score}', x=180, y=2, color=(255, 255, 0))

        # Draw ammo display with color coding
        ammo1_color = (255, 255, 255) if self.players[0].ammo > 0 else (255, 0, 0)
        ammo2_color = (255, 255, 255) if self.players[1].ammo > 0 else (255, 0, 0)

        ledwall.drawText(f'AMMO: {self.players[0].ammo}', x=2, y=15, color=ammo1_color)
        ledwall.drawText(f'AMMO: {self.players[1].ammo}', x=180, y=15, color=ammo2_color)

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            for i, keys in enumerate([controls.PLAYER_1_KEYS, controls.PLAYER_2_KEYS]):
                if e.key == keys[controls.DIR_LEFT]:
                    self.players[i].moveLeft()
                elif e.key == keys[controls.DIR_RIGHT]:
                    self.players[i].moveRight()
                elif e.key == keys[controls.DIR_UP]:
                    self.players[i].moveUp()
                elif e.key == keys[controls.DIR_DOWN]:
                    self.players[i].moveDown()

                elif e.key == keys[controls.FIRE]:
                    self.players[i].shoot(i)

        elif e.type == pygame.KEYUP:
            for i, keys in enumerate([controls.PLAYER_1_KEYS, controls.PLAYER_2_KEYS]):
                if e.key == keys[controls.DIR_LEFT]:
                    self.players[i].stopLeft()
                elif e.key == keys[controls.DIR_RIGHT]:
                    self.players[i].stopRight()
                elif e.key == keys[controls.DIR_UP]:
                    self.players[i].stopUp()
                elif e.key == keys[controls.DIR_DOWN]:
                    self.players[i].stopDown()

                elif e.key == keys[controls.FIRE]:
                    self.players[i].stopShooting()

    def update(self):
        for player in self.players:
            player.update()

        for obj in self.objects:
            obj.update()

        # Check for collisions
        checkCollisions()

        # Check for weapon pickups
        checkWeaponPickup()

        # Spawn weapon drops periodically
        self.weapon_drop_timer += 1
        if self.weapon_drop_timer >= 300:  # Spawn every 5 seconds (300 frames at 60 FPS)
            import random
            # Only spawn if there aren't too many weapon drops already
            weapon_drops = [obj for obj in self.objects if isinstance(obj, WeaponDrop)]
            if len(weapon_drops) < 3:  # Max 3 weapon drops on map
                if random.random() < 0.7:  # 70% chance to spawn
                    spawnWeaponDrop()
            self.weapon_drop_timer = 0

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
         'o': Sprite('gfx/stone1.png'),
         ' ': None,
         }

PLAYER_1_SPRITE = createAnimatedSprite('gfx/player1.png')
PLAYER_2_SPRITE = createAnimatedSprite('gfx/player2.png')

BULLET_SPRITE = Sprite('gfx/bullet.png')
MUNITION_SPRITE = Sprite('gfx/munition.png')

print('loading sfx...')
SFX_GUNSHOT = pygame.mixer.Sound("sfx/Gunshot.wav")
SFX_FOOTSTEP = pygame.mixer.Sound("sfx/Footstep.wav")
SFX_RICOCHET = pygame.mixer.Sound("sfx/Ricochet.wav")
SFX_PLAYER_HIT = pygame.mixer.Sound("sfx/Wilhelm_Scream.wav")
SFX_EXPLOSION = pygame.mixer.Sound("sfx/Explosion.wav")

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
gameOverScreen = GameOverScreen()

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
