"""
Explosion effect class for Drunk Duel.
Creates particle-based explosion effects.
"""

import random
import pygame
import ledwall
from object import Object

# Override print function
import ledwall
print = ledwall.print


class Explosion(Object):
    """A particle-based explosion effect."""

    def __init__(self, xpos, ypos):
        # Create a simple explosion sprite (we'll draw particles)
        explosion_surface = pygame.Surface((16, 16), flags=pygame.SRCALPHA)
        super().__init__(xpos, ypos, None)  # We'll handle drawing ourselves

        self.particles = []
        self.lifetime = 30  # frames
        self.age = 0

        # Create particles
        for i in range(8):
            particle = {
                'x': xpos + 8,  # TILE_WIDTH // 2
                'y': ypos + 8,  # TILE_HEIGHT // 2
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': random.randint(15, 25)
            }
            self.particles.append(particle)

    def update(self):
        """Update explosion particles and lifetime."""
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
            import game_state
            game_state.gameScreen.removeObject(self)

    def draw(self, output):
        """Draw explosion particles."""
        # Draw particles as colored pixels
        for particle in self.particles:
            if particle['life'] > 0:
                # Color fades from yellow to red
                life_ratio = particle['life'] / 25.0
                color = (255, int(255 * life_ratio), 0)
                x, y = int(particle['x']), int(particle['y'])
                if 0 <= x < ledwall.SCR_W and 0 <= y < ledwall.SCR_H:
                    pygame.draw.circle(output, color, (x, y), 2)