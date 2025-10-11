"""
Bird object module for Drunk Duel.
Contains animated birds that fly across the screen randomly.
"""

import random
import game_state
from object import Object
from sprite import createAnimatedSprite

# Override print function
import ledwall
print = ledwall.print


class Bird(Object):
    """An animated bird that flies across the screen."""
    
    def __init__(self, xpos, ypos, flying_right=None):
        # Create the animated sprite with both left and right animations
        self.sprite = createAnimatedSprite('gfx/birdfly1.png', 16, 16)
        super().__init__(xpos, ypos, self.sprite)
        
        # Set flying direction (random if not specified)
        if flying_right is None:
            self.flying_right = random.choice([True, False])
        else:
            self.flying_right = flying_right
        
        # Set animation based on direction
        if self.flying_right:
            self.sprite.select(1)  # Row 1 = flying right
        else:
            self.sprite.select(0)  # Row 0 = flying left
            
        # Set animation speed and start
        self.sprite.speed = 8
        self.sprite.start()
        
        # Set flying speed (pixels per frame)
        self.speed = random.uniform(0.5, 1.5)  # Random speed between 0.5 and 1.5 pixels per frame
        
        # Track if bird is still on screen
        self.active = True
        
    def update(self):
        """Update the bird's position as it flies across the screen."""
        if not self.active:
            return
            
        # Move the bird horizontally
        if self.flying_right:
            self.xpos += self.speed
            # Remove bird when it flies off the right edge
            if self.xpos > game_state.output.get_width():
                self.active = False
        else:
            self.xpos -= self.speed
            # Remove bird when it flies off the left edge  
            if self.xpos < -16:  # -16 because sprite is 16px wide
                self.active = False
    
    def is_active(self):
        """Check if the bird is still active (on screen)."""
        return self.active