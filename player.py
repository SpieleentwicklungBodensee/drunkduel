
"""
Player class and related functionality for Drunk Duel.
Handles player movement, collision detection, and interactions.
"""
import controls
import config
from object import Object
from sprite import createAnimatedSprite
from game_logic import spawnBullet
from sound_manager import playFootstepSound, SFX_GUNSHOT

# Load player sprites
PLAYER_1_SPRITE = None
PLAYER_2_SPRITE = None


def load_player_sprites():
    """Load player sprites if not already loaded."""
    global PLAYER_1_SPRITE, PLAYER_2_SPRITE
    if PLAYER_1_SPRITE is None:
        PLAYER_1_SPRITE = createAnimatedSprite('gfx/player1.png')
    if PLAYER_2_SPRITE is None:
        PLAYER_2_SPRITE = createAnimatedSprite('gfx/player2.png')
    return PLAYER_1_SPRITE, PLAYER_2_SPRITE

class Player(Object):
    def __init__(self, xpos, ypos, sprite):
        super().__init__(xpos, ypos, sprite)

        self.xdir = 0
        self.ydir = 0
        self.speed = 1.5

        self.facedir = controls.DIR_DOWN

        self.score = 0
        self.ammo = config.INITIAL_AMMO
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

    def stopMoving(self):
        self.xdir = 0
        self.ydir = 0
        self.sprite.stop()

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

        # Get bullet sprite from game state
        import game_state
        if hasattr(game_state, 'bullet_sprite'):
            bullet_sprite = game_state.bullet_sprite
        else:
            # Fallback: load directly
            from sprite import Sprite
            bullet_sprite = Sprite('gfx/bullet.png')

        spawnBullet(self.xpos, self.ypos, bulletxdir, player_index, bullet_sprite)
        SFX_GUNSHOT.play(loops=0)

    def stopShooting(self):
        self.showGun = False

    def update(self):
        import game_state
        from game_state import TILE_WIDTH, TILE_HEIGHT

        new_xpos = self.xpos
        new_ypos = self.ypos

        new_xdir = self.xdir
        new_ydir = self.ydir

        tempspeed = self.speed

        # collision with level border:
        if new_xpos < 0:
            new_xpos = 0
            new_xdir = 0

        if new_xpos > (game_state.level.getWidth() -1) * TILE_WIDTH:
            new_xpos = (game_state.level.getWidth() -1) * TILE_WIDTH
            new_xdir = 0

        if new_ypos < 0:
            new_ypos = 0
            new_ydir = 0

        if new_ypos > (game_state.level.getHeight() -1) * TILE_HEIGHT:
            new_ypos = (game_state.level.getHeight() -1) * TILE_HEIGHT
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

        t1 = game_state.level.getTile(x1, y1)
        t2 = game_state.level.getTile(x2, y1)
        t3 = game_state.level.getTile(x1, y2)
        t4 = game_state.level.getTile(x2, y2)

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

            if game_state.tick % 8 == 0:
                playFootstepSound()


