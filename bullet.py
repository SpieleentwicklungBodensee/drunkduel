"""
Bullet class for Drunk Duel.
Handles bullet movement, collision detection, and behavior.
"""

import random

import ledwall
import game_state
import config
from object import Object
from sound_manager import SFX_RICOCHET, SFX_EXPLOSION
from game_state import TILE_WIDTH, TILE_HEIGHT
from explosion import Explosion
from weapon_drop import WeaponDrop

# Override print function
import ledwall
print = ledwall.print

class Bullet(Object):
    """A bullet fired by a player."""

    def __init__(self, xpos, ypos, bullet_sprite):
        super().__init__(xpos, ypos, bullet_sprite)

        self.xdir = 0
        self.ydir = 0  # Add vertical direction support
        self.speed = 4
        self.shooter_index = -1  # Will be set when spawned
        self.damage = 25  # Base damage, will be modified by drunk level
        self.drunk_damage_modifier = 1.0  # Will be set when spawned

    def get_total_damage(self):
        """Berechnet den Gesamtschaden der Kugel."""
        if config.ALCOHOL_ENABLED:
            print("Drunk Damage Modifier:", self.drunk_damage_modifier)
            return int(self.damage * self.drunk_damage_modifier)
        else:
            #Kill player instantly if alcohol is disabled
            return 1000

    def update(self):
        """Update bullet position and check for collisions."""

        self.xpos += self.xdir * self.speed
        self.ypos += self.ydir * self.speed

        # Check for collision with tiles
        tile_x = int(self.xpos // TILE_WIDTH)
        tile_y = int(self.ypos // TILE_HEIGHT)

        if 0 <= tile_x < game_state.level.getWidth() and 0 <= tile_y < game_state.level.getHeight():
            tile = game_state.level.getTile(tile_x, tile_y)
            if tile == 'Y':  # Hit a cactus - explode it
                self._explode_cactus(tile_x, tile_y)
                return
            elif tile in ['#', 'o', 'F']:  # Hit fence, stone, or invisible wall - just bounce/disappear
                self._hit_solid_object()
                return

        # Remove bullet if it goes off screen
        if (self.xpos < -TILE_WIDTH or self.xpos > ledwall.SCR_W or
            self.ypos < -TILE_HEIGHT or self.ypos > ledwall.SCR_H):
            self._remove_bullet()

    def _explode_cactus(self, tile_x, tile_y):
        """Handle cactus explosion logic."""


        # Create explosion effect
        explosion = Explosion(tile_x * TILE_WIDTH, tile_y * TILE_HEIGHT)
        game_state.gameScreen.addObject(explosion)

        # Remove the cactus from the map
        game_state.level.setTile(tile_x, tile_y, ' ')

        # Schedule a new cactus to respawn after 5-10 seconds
        game_state.gameScreen.schedule_cactus_respawn()

        # Play explosion sound
        SFX_EXPLOSION.play()

        # 30% chance to spawn a weapon drop where the cactus was (but not in duck hunt mode)
        if not getattr(config, 'DUCK_HUNT_MODE', False) and random.random() < 0.3:
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