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