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
        
        # Landing behavior
        self.landing_chance = 0.005  # Small chance per frame to consider landing (increased from 0.002)
        self.last_landing_check = 0  # Cooldown for landing checks
        
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
            
            # Check if bird should land on a fence
            self._check_fence_landing()
                    
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
    
    def _check_fence_landing(self):
        """Check if the bird should land on a nearby fence or cactus."""
        import game_state
        
        # Only check occasionally and with cooldown
        if (random.random() > self.landing_chance or 
            game_state.tick - self.last_landing_check < 60):  # 1 second cooldown (reduced from 2)
            return
            
        self.last_landing_check = game_state.tick
        
        # Find nearby fence or cactus tiles
        current_tile_x = int(self.xpos / 16)  # TILE_WIDTH
        current_tile_y = int(self.ypos / 16)  # TILE_HEIGHT
        
        # Check tiles in a small area around the bird
        for dy in range(-1, 3):  # Check slightly below and above
            for dx in range(-2, 3):  # Check a few tiles horizontally
                check_x = current_tile_x + dx
                check_y = current_tile_y + dy
                
                # Make sure we're within level bounds
                if (0 <= check_x < game_state.level.getWidth() and 
                    0 <= check_y < game_state.level.getHeight()):
                    
                    tile = game_state.level.getTile(check_x, check_y)
                    
                    if tile in ['#', 'Y']:  # Found a fence or cactus
                        # Check if this position is free of other birds
                        if self._is_fence_position_free(check_x, check_y):
                            # Land on this fence or cactus!
                            self._land_on_tile(check_x, check_y, tile)
                            return
    
    def _is_fence_position_free(self, fence_x, fence_y):
        """Check if a fence position is free of other fence birds."""
        fence_pixel_x = fence_x * 16  # TILE_WIDTH
        fence_pixel_y = fence_y * 16 - 4  # TILE_HEIGHT, slightly above fence
        
        # Check if there's already a fence bird at this position
        for obj in game_state.gameScreen.objects:
            if isinstance(obj, FenceBird) and obj.state == "sitting":
                if (abs(obj.xpos - fence_pixel_x) < 12 and 
                    abs(obj.ypos - fence_pixel_y) < 12):
                    return False
        return True
    
    def _land_on_tile(self, tile_x, tile_y, tile_type):
        """Convert this flying bird into a fence bird on the specified tile."""
        # Calculate tile position
        tile_pixel_x = tile_x * 16  # TILE_WIDTH  
        tile_pixel_y = tile_y * 16 - 4  # TILE_HEIGHT, slightly above tile
        
        # Create a new fence bird at the tile position
        fence_bird = FenceBird(tile_pixel_x, tile_pixel_y, tile_x, tile_y, tile_type)
        game_state.gameScreen.addObject(fence_bird)
        
        # Remove this flying bird
        self.active = False


class FenceBird(Object):
    """A bird that sits on fences or cacti and can be shot down."""
    
    def __init__(self, xpos, ypos, tile_x=None, tile_y=None, tile_type='#'):
        # Create a static sprite for the fence bird
        from sprite import Sprite
        self.sprite = Sprite('gfx/bird1_nowood.png')
        super().__init__(xpos, ypos, self.sprite)
        
        # Track which tile the bird is sitting on
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.tile_type = tile_type  # '#' for fence, 'Y' for cactus
        
        # Track bird state
        self.state = "sitting"  # "sitting", "scared_flying", "falling", "exploded"
        self.active = True
        self.fall_speed = 0.0  # Vertical falling speed
        self.gravity = 0.2  # Gravity acceleration
        
        # Scare behavior
        self.scare_radius = 64  # 4 tiles * 16 pixels per tile
        self.flying_right = random.choice([True, False])  # Random flee direction
        self.flee_speed = random.uniform(1.0, 2.0)  # Speed when scared and flying
        
    def update(self):
        """Update the fence bird's state."""
        if not self.active:
            return
        
        if self.state == "sitting":
            # Check for nearby bullets that might scare the bird
            self._check_for_scary_bullets()
            
            # Check if the tile the bird is sitting on still exists
            if self.tile_x is not None and self.tile_y is not None:
                if self._check_if_tile_destroyed():
                    # Tile was destroyed, fly away!
                    self._get_scared_by_destruction()
            
        elif self.state == "scared_flying":
            # Bird is flying away after being scared
            if self.flying_right:
                self.xpos += self.flee_speed
                # Remove bird when it flies off the right edge
                if self.xpos > game_state.output.get_width():
                    self.active = False
            else:
                self.xpos -= self.flee_speed
                # Remove bird when it flies off the left edge
                if self.xpos < -16:
                    self.active = False
            
        elif self.state == "falling":
            # Bird is falling - apply gravity
            self.fall_speed += self.gravity
            self.ypos += self.fall_speed
            
            # Check if bird hit the ground (bottom of game area)
            game_height = game_state.level.getHeight() * 16  # TILE_HEIGHT
            if self.ypos >= game_height - 16:  # Hit ground
                self._explode()
    
    def get_shot(self):
        """Called when the fence bird is hit by a bullet."""
        if self.state in ["sitting", "scared_flying"]:
            self.state = "falling"
            self.fall_speed = 1.0  # Start with some initial downward velocity
    
    def _check_for_scary_bullets(self):
        """Check if there are any bullets nearby that would scare the bird."""
        from bullet import Bullet
        
        # Check all bullets in the game
        for obj in game_state.gameScreen.objects:
            if isinstance(obj, Bullet):
                # Calculate distance from bullet to bird
                dx = obj.xpos - self.xpos
                dy = obj.ypos - self.ypos
                distance = (dx * dx + dy * dy) ** 0.5  # Pythagorean distance
                
                if distance <= self.scare_radius:
                    # Bullet is close enough to scare the bird!
                    self._get_scared(dx, dy)
                    return
    
    def _get_scared(self, bullet_dx, bullet_dy):
        """Make the bird fly away when scared by a bullet."""
        self.state = "scared_flying"
        
        # Fly away from the bullet
        if bullet_dx > 0:  # Bullet is to the right, fly left
            self.flying_right = False
        else:  # Bullet is to the left, fly right
            self.flying_right = True
        
        # Convert to flying bird sprite for the scared flight
        self.sprite = createAnimatedSprite('gfx/birdfly1.png', 16, 16)
        
        # Set animation based on direction
        if self.flying_right:
            self.sprite.select(1)  # Row 1 = flying right
        else:
            self.sprite.select(0)  # Row 0 = flying left
            
        # Set animation speed and start
        self.sprite.speed = 8
        self.sprite.start()
            
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
        """Check if the bird is still active."""
        return self.active
    
    def get_bounds(self):
        """Get bounding rectangle for collision detection."""
        return {
            'x': self.xpos,
            'y': self.ypos,
            'width': 16,
            'height': 16
        }
    
    def _check_if_tile_destroyed(self):
        """Check if the tile the bird is sitting on has been destroyed."""
        if (0 <= self.tile_x < game_state.level.getWidth() and 
            0 <= self.tile_y < game_state.level.getHeight()):
            current_tile = game_state.level.getTile(self.tile_x, self.tile_y)
            # If the tile changed from what we were sitting on, it was destroyed
            return current_tile != self.tile_type
        return True  # If coordinates are invalid, assume destroyed
    
    def _get_scared_by_destruction(self):
        """Make the bird fly away when its tile is destroyed."""
        self.state = "scared_flying"
        
        # Fly in a random direction when scared by destruction
        self.flying_right = random.choice([True, False])
        
        # Convert to flying bird sprite for the scared flight
        self.sprite = createAnimatedSprite('gfx/birdfly1.png', 16, 16)
        
        # Set animation based on direction
        if self.flying_right:
            self.sprite.select(1)  # Row 1 = flying right
        else:
            self.sprite.select(0)  # Row 0 = flying left
            
        # Set animation speed and start
        self.sprite.speed = 8
        self.sprite.start()