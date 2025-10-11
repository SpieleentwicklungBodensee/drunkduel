"""
Health powerup module for Drunk Duel.
Handles health kit pickups that restore player health.
"""

import random
from object import Object

# Override print function
import ledwall
print = ledwall.print


class HealthPowerup(Object):
    def __init__(self, xpos, ypos, sprite):
        super().__init__(xpos, ypos, sprite)
        self.lifetime = 600  # Lebensdauer in Frames (10 Sekunden bei 60 FPS)
        self.blink_timer = 0
        self.visible = True
        self.health_amount = random.randint(20, 40)  # Zufällige Heilmenge

    def update(self):
        self.lifetime -= 1

        # Blinken in den letzten 3 Sekunden
        if self.lifetime < 180:
            self.blink_timer += 1
            if self.blink_timer >= 10:  # Alle 10 Frames blinken
                self.visible = not self.visible
                self.blink_timer = 0

        # Powerup verschwindet nach Ablauf der Zeit
        if self.lifetime <= 0:
            return True  # Signal zum Entfernen
        return False

    def draw(self, output):
        if self.visible:
            super().draw(output)

    def get_health_amount(self):
        """Gibt die Heilmenge zurück, die dieses Medkit verleiht."""
        return self.health_amount