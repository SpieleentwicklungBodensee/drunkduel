"""
Beer powerup module for Drunk Duel.
Handles beer bottle pickups that increase player alcohol levels.
"""

import random
from object import Object

class BeerPowerup(Object):
    def __init__(self, xpos, ypos, sprite):
        super().__init__(xpos, ypos, sprite)
        self.lifetime = 600  # Lebensdauer in Frames (10 Sekunden bei 60 FPS)
        self.blink_timer = 0
        self.visible = True
        self.alcohol_amount = random.uniform(0.2, 0.4)  # Zufällige Alkohol-Menge
        
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
            
    def get_alcohol_amount(self):
        """Gibt die Alkohol-Menge zurück, die dieses Bier verleiht."""
        return self.alcohol_amount