"""
Bullet class for Drunk Duel.
Handles bullet movement, collision detection, and behavior.
"""

import random

import ledwall
import game_state
from object import Object
from sound_manager import SFX_RICOCHET
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT
from explosion import Explosion
from weapon_drop import WeaponDrop
from sound_manager import SFX_EXPLOSION

class Bullet(Object):
    """A bullet fired by a player."""
    
    def __init__(self, xpos, ypos, bullet_sprite):
        super().__init__(xpos, ypos, bullet_sprite)

        self.xdir = 0
        self.speed = 4
        self.shooter_index = -1  # Will be set when spawned

    def update(self):
        """Update bullet position and check for collisions."""
        
        
        self.xpos += self.xdir * self.speed

        # Check for collision with tiles
        tile_x = int(self.xpos // TILE_WIDTH)
        tile_y = int(self.ypos // TILE_HEIGHT)

        if 0 <= tile_x < game_state.level.getWidth() and 0 <= tile_y < game_state.level.getHeight():
            tile = game_state.level.getTile(tile_x, tile_y)
            if tile == 'Y':  # Hit a cactus - explode it
                self._explode_cactus(tile_x, tile_y)
                return
            elif tile in ['#', 'o']:  # Hit fence or stone - just bounce/disappear
                self._hit_solid_object()
                return

        # Remove bullet if it goes off screen
        if self.xpos < -TILE_WIDTH or self.xpos > ledwall.SCR_W:
            self._remove_bullet()

    def _explode_cactus(self, tile_x, tile_y):
        """Handle cactus explosion logic."""

        
        # Create explosion effect
        explosion = Explosion(tile_x * TILE_WIDTH, tile_y * TILE_HEIGHT)
        game_state.gameScreen.addObject(explosion)

        # Remove the cactus from the map
        game_state.level.setTile(tile_x, tile_y, ' ')

        # Play explosion sound
        SFX_EXPLOSION.play()

        # 30% chance to spawn a weapon drop where the cactus was
        if random.random() < 0.3:
            if hasattr(game_state, 'munition_sprite'):
                weapon_drop = WeaponDrop(tile_x * TILE_WIDTH, tile_y * TILE_HEIGHT, game_state.munition_sprite)
                game_state.gameScreen.addObject(weapon_drop)

        # Remove the bullet
        self._remove_bullet()

    def _hit_solid_object(self):
        """Handle collision with solid objects."""
        SFX_RICOCHET.play()
        self._remove_bullet()

    def _remove_bullet(self):
        """Remove this bullet from the game."""
        game_state.gameScreen.removeObject(self)