"""
Bird object module for Drunk Duel.
Contains animated birds that fly across the screen randomly and can be shot down.
"""

import random
import game_state
from object import Object
from sprite import createAnimatedSprite
from explosion import Explosion
from sound_manager import SFX_EXPLOSION

# Override print function
import ledwall
print = ledwall.print


class Bird(Object):
    """An animated bird that flies across the screen and can be shot down."""
    
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
        
        # Track bird state
        self.state = "flying"  # "flying", "falling", "exploded"
        self.active = True
        self.fall_speed = 0.0  # Vertical falling speed
        self.gravity = 0.2  # Gravity acceleration
        
    def update(self):
        """Update the bird's position and state."""
        if not self.active:
            return
            
        if self.state == "flying":
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
                    
        elif self.state == "falling":
            # Bird is falling - apply gravity
            self.fall_speed += self.gravity
            self.ypos += self.fall_speed
            
            # Stop animation when falling
            self.sprite.stop()
            
            # Check if bird hit the ground (bottom of game area)
            game_height = game_state.level.getHeight() * 16  # TILE_HEIGHT
            if self.ypos >= game_height - 16:  # Hit ground
                self._explode()
    
    def get_shot(self):
        """Called when the bird is hit by a bullet."""
        if self.state == "flying":
            self.state = "falling"
            self.fall_speed = 0.0  # Start falling from rest
            
    def _explode(self):
        """Create explosion effect when bird hits ground."""
        self.state = "exploded"
        self.active = False
        
        # Create explosion at bird's position
        explosion = Explosion(self.xpos, self.ypos)
        game_state.gameScreen.addObject(explosion)
        
        # Play explosion sound
        SFX_EXPLOSION.play()
    
    def is_active(self):
        """Check if the bird is still active (on screen)."""
        return self.active
    
    def get_bounds(self):
        """Get bounding rectangle for collision detection."""
        return {
            'x': self.xpos,
            'y': self.ypos,
            'width': 16,
            'height': 16
        }