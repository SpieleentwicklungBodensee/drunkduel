"""
Weapon drop class for Drunk Duel.
Handles ammunition pickups that appear in the game.
"""

import math

from object import Object

# Override print function
import ledwall
print = ledwall.print



class WeaponDrop(Object):
    """An ammunition pickup that players can collect."""

    def __init__(self, xpos, ypos, munition_sprite):
        super().__init__(xpos, ypos, munition_sprite)
        self.ammo_amount = 3  # How much ammo this drop gives
        self.bob_offset = 0   # For floating animation

    def update(self):
        """Update floating animation."""
        # Floating animation
        self.bob_offset += 0.1

    def draw(self, output):
        """Draw weapon drop with bobbing animation."""
        # Draw with slight vertical bobbing animation
        bob_y = self.ypos + math.sin(self.bob_offset) * 2
        self.sprite.draw(output, self.xpos, int(bob_y))

    def get_hit(self):
        """Called when the weapon drop is hit by a bullet - explodes and creates explosion."""
        # Create explosion effect at weapon drop location
        from explosion import Explosion
        import game_state
        explosion = Explosion(self.xpos, self.ypos)
        game_state.gameScreen.addObject(explosion)
        
        # Play explosion sound
        from sound_manager import SFX_EXPLOSION
        SFX_EXPLOSION.play()
        
        # Remove the weapon drop
        game_state.gameScreen.removeObject(self)

    def get_bounds(self):
        """Get bounding rectangle for collision detection."""
        from game_state import TILE_WIDTH, TILE_HEIGHT
        return {
            'x': self.xpos,
            'y': self.ypos + math.sin(self.bob_offset) * 2,  # Account for bobbing animation
            'width': TILE_WIDTH,
            'height': TILE_HEIGHT
        }