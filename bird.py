"""
Bird object module for Drunk Duel.
Contains animated birds that fly across the screen randomly and can be shot down.
"""

import random
import game_state
from object import Object
from sprite import createAnimatedSprite
from explosion import Explosion
from sound_manager import SFX_EXPLOSION, SFX_BIRD_HIT, SFX_BIRD_EXPLODING, SFX_BIRD_LAUNCH

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
        self.flee_speed = random.uniform(1.0, 2.0)  # Speed when scared and flying
        
        # Track bird state
        self.state = "flying"  # "flying", "landing", "falling", "exploded", "circling", "scared_flying"
        self.active = True
        self.fall_speed = 0.0  # Vertical falling speed
        self.gravity = 0.2  # Gravity acceleration
        
        # Circling behavior parameters
        self.circling_target_x = 0
        self.circling_target_y = 0
        self.circle_radius = random.uniform(30, 60)  # Radius of circling motion
        self.circle_angle = random.uniform(0, 6.28)  # Starting angle (0 to 2π)
        self.circle_speed = random.uniform(0.02, 0.05)  # Angular speed
        
        # Precalculated landing behavior
        self.has_landing_target = False
        self.landing_target_tile_x = None
        self.landing_target_tile_y = None
        self.landing_target_tile_type = None
        self.landing_target_pixel_x = None
        self.landing_target_pixel_y = None
        
        # Landing animation variables
        self.landing_start_x = 0
        self.landing_start_y = 0
        self.landing_progress = 0.0
        self.landing_duration = 30  # frames to complete landing
        
        # Determine if this bird should have a landing target
        self._maybe_choose_landing_target()
        
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
            
            # Check if bird should start landing
            self._check_for_landing()
            
        elif self.state == "landing":
            # Bird is smoothly moving to landing position
            self.landing_progress += 1.0 / self.landing_duration
            
            if self.landing_progress >= 1.0:
                # Landing complete - create fence bird and remove this flying bird
                self._complete_landing()
            else:
                # Interpolate position smoothly
                t = self.landing_progress
                # Use easing for more natural movement (ease out)
                t = 1 - (1 - t) ** 2
                
                self.xpos = self.landing_start_x + (self.landing_target_pixel_x - self.landing_start_x) * t
                self.ypos = self.landing_start_y + (self.landing_target_pixel_y - self.landing_start_y) * t
                    
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
                
        elif self.state == "circling":
            # Bird is circling around a target point
            import math
            
            # Update the angle for circular motion
            self.circle_angle += self.circle_speed
            
            # Calculate new position based on circular motion
            self.xpos = self.circling_target_x + math.cos(self.circle_angle) * self.circle_radius
            self.ypos = self.circling_target_y + math.sin(self.circle_angle) * self.circle_radius
            
            # Update animation direction based on movement
            prev_angle = self.circle_angle - self.circle_speed
            prev_x = self.circling_target_x + math.cos(prev_angle) * self.circle_radius
            if self.xpos > prev_x:
                # Moving right
                if not self.flying_right:
                    self.flying_right = True
                    self.sprite.select(1)  # Row 1 = flying right
            else:
                # Moving left
                if self.flying_right:
                    self.flying_right = False
                    self.sprite.select(0)  # Row 0 = flying left
                    
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
    
    def get_shot(self):
        """Called when the bird is hit by a bullet."""
        if self.state in ["flying", "landing", "circling", "scared_flying"]:
            # Play bird hit sound
            SFX_BIRD_HIT.play()
            self.state = "falling"
            self.fall_speed = 0.0  # Start falling from rest
    
    def start_circling(self, target_x, target_y):
        """Start circling around the specified target position."""
        self.state = "circling"
        self.circling_target_x = target_x
        self.circling_target_y = target_y
        
        # Set initial position on the circle
        import math
        self.xpos = target_x + math.cos(self.circle_angle) * self.circle_radius
        self.ypos = target_y + math.sin(self.circle_angle) * self.circle_radius
            
    def _explode(self):
        """Create explosion effect when bird hits ground."""
        self.state = "exploded"
        self.active = False
        
        # Create explosion at bird's position
        explosion = Explosion(self.xpos, self.ypos)
        game_state.gameScreen.addObject(explosion)
        
        # Play bird explosion sound
        SFX_BIRD_EXPLODING.play()
    
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
    
    def _maybe_choose_landing_target(self):
        """Decide if this bird should have a landing target and choose one."""
        # 30% chance for a flying bird to have a landing target
        if random.random() > 0.3:
            return
            
        # Find all available perches
        available_perches = self._find_available_perches()
        if not available_perches:
            return
            
        # Choose a perch that makes sense for the bird's flight direction
        suitable_perches = []
        for tile_x, tile_y, tile_type in available_perches:
            tile_pixel_x = tile_x * 16
            
            # For right-flying birds, only consider perches ahead (to the right)
            # For left-flying birds, only consider perches ahead (to the left)
            if self.flying_right and tile_pixel_x > self.xpos:
                suitable_perches.append((tile_x, tile_y, tile_type))
            elif not self.flying_right and tile_pixel_x < self.xpos:
                suitable_perches.append((tile_x, tile_y, tile_type))
        
        if suitable_perches:
            # Choose a random suitable perch
            self.landing_target_tile_x, self.landing_target_tile_y, self.landing_target_tile_type = random.choice(suitable_perches)
            self.landing_target_pixel_x = self.landing_target_tile_x * 16
            self.landing_target_pixel_y = self.landing_target_tile_y * 16 - 4
            self.has_landing_target = True
            
            # Adjust spawn Y position to be near the landing target (±2 tiles)
            self._adjust_spawn_y_for_target()
    
    def _find_available_perches(self):
        """Find all available fence and cactus tiles that don't have birds."""
        if not hasattr(game_state, 'level') or not game_state.level:
            return []
            
        available_perches = []
        
        # Find all fence and cactus tiles
        for y in range(game_state.level.getHeight()):
            for x in range(game_state.level.getWidth()):
                tile = game_state.level.getTile(x, y)
                if tile in ['#', 'Y']:  # Fence or cactus
                    # Check if position is free
                    if self._is_perch_position_free(x, y):
                        available_perches.append((x, y, tile))
        
        return available_perches
    
    def _is_perch_position_free(self, tile_x, tile_y):
        """Check if a perch position is free of other fence birds."""
        pixel_x = tile_x * 16
        pixel_y = tile_y * 16 - 4
        
        # Check if there's already a fence bird at this position
        for obj in game_state.gameScreen.objects:
            if isinstance(obj, FenceBird) and obj.state == "sitting":
                if (abs(obj.xpos - pixel_x) < 12 and 
                    abs(obj.ypos - pixel_y) < 12):
                    return False
        return True
    
    def _check_for_landing(self):
        """Check if the bird should start landing at its target."""
        if not self.has_landing_target:
            return
            
        # Check if we're close enough to the target to start landing
        distance_to_target = abs(self.xpos - self.landing_target_pixel_x)
        
        # Start landing when we're within 32 pixels of the target
        if distance_to_target <= 32:
            # Make sure the target is still available
            if self._is_perch_position_free(self.landing_target_tile_x, self.landing_target_tile_y):
                self._start_landing()
            else:
                # Target is no longer available, continue flying
                self.has_landing_target = False
    
    def _start_landing(self):
        """Start the landing animation."""
        self.state = "landing"
        self.landing_start_x = self.xpos
        self.landing_start_y = self.ypos
        self.landing_progress = 0.0
        
        # Slow down the bird during landing
        self.sprite.speed = 4  # Slower animation during landing
    
    def _adjust_spawn_y_for_target(self):
        """Adjust the bird's Y position to be within ±2 tiles of the landing target."""
        target_y = self.landing_target_pixel_y
        
        # Calculate Y range: ±2 tiles (32 pixels) from target
        min_y = max(16, target_y - 32)  # Don't go above screen top
        max_y = min(target_y + 32, game_state.level.getHeight() * 16 - 32)  # Don't go below game area
        
        # Set bird's Y position randomly within this range
        self.ypos = random.uniform(min_y, max_y)
    
    def _complete_landing(self):
        """Complete the landing by creating a fence bird and removing this flying bird."""
        # Create a new fence bird at the target position
        fence_bird = FenceBird(self.landing_target_pixel_x, self.landing_target_pixel_y, 
                              self.landing_target_tile_x, self.landing_target_tile_y, self.landing_target_tile_type)
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
        self.state = "sitting"  # "sitting", "scared_flying", "falling", "exploded", "circling"
        self.active = True
        self.fall_speed = 0.0  # Vertical falling speed
        self.gravity = 0.2  # Gravity acceleration
        
        # Circling behavior parameters
        self.circling_target_x = 0
        self.circling_target_y = 0
        self.circle_radius = random.uniform(30, 60)  # Radius of circling motion
        self.circle_angle = random.uniform(0, 6.28)  # Starting angle (0 to 2π)
        self.circle_speed = random.uniform(0.02, 0.05)  # Angular speed
        self.flying_right = random.choice([True, False])  # Direction for circling animation
        
        # Determine if bird should be flipped based on map position
        # The texture faces left by default, so flip it if on the right half
        map_width = game_state.level.getWidth() * 16  # Convert to pixels

        # Determine if bird should be flipped based on map position
        self.should_flip = not (self.xpos > (map_width / 2))
        
        # Scare behavior
        self.scare_radius = 64  # 4 tiles * 16 pixels per tile
        self.flying_right = random.choice([True, False])  # Random flee direction
        self.flee_speed = random.uniform(1.0, 2.0)  # Speed when scared and flying
        
        # Random fly-away behavior
        self.sitting_timer = 0  # How long the bird has been sitting
        self.fly_away_time = random.randint(300, 1200)  # 5-20 seconds at 60 FPS
        
    def draw(self, output):
        """Custom draw method to handle sprite flipping based on position."""
        if self.state == "sitting" and self.should_flip:
            # Flip the sprite horizontally for birds on the right half
            import pygame
            flipped_surface = pygame.transform.flip(self.sprite.surface, True, False)
            output.blit(flipped_surface, (self.xpos, self.ypos))
        else:
            # Use normal sprite drawing
            self.sprite.draw(output, self.xpos, self.ypos)
        
    def update(self):
        """Update the fence bird's state."""
        if not self.active:
            return
        
        if self.state == "sitting":
            # Increment sitting timer
            self.sitting_timer += 1
            
            # Check for nearby bullets that might scare the bird
            self._check_for_scary_bullets()
            
            # Check if the tile the bird is sitting on still exists
            if self.tile_x is not None and self.tile_y is not None:
                if self._check_if_tile_destroyed():
                    # Tile was destroyed, fly away!
                    self._get_scared_by_destruction()
                    return
            
            # Random chance to fly away after sitting for a while
            if self.sitting_timer >= self.fly_away_time:
                # 30% chance per frame after the fly_away_time has passed
                if random.random() < 0.005:  # 0.5% chance per frame = ~30% chance per second
                    self._fly_away_randomly()
            
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
                
        elif self.state == "circling":
            # Bird is circling around a target point
            import math
            
            # Update the angle for circular motion
            self.circle_angle += self.circle_speed
            
            # Calculate new position based on circular motion
            self.xpos = self.circling_target_x + math.cos(self.circle_angle) * self.circle_radius
            self.ypos = self.circling_target_y + math.sin(self.circle_angle) * self.circle_radius
            
            # Update animation direction based on movement
            prev_angle = self.circle_angle - self.circle_speed
            prev_x = self.circling_target_x + math.cos(prev_angle) * self.circle_radius
            if self.xpos > prev_x:
                self.flying_right = True
            else:
                self.flying_right = False
    
    def get_shot(self):
        """Called when the fence bird is hit by a bullet."""
        if self.state in ["sitting", "scared_flying", "circling"]:
            # Play bird hit sound
            SFX_BIRD_HIT.play()
            self.state = "falling"
            self.fall_speed = 1.0  # Start with some initial downward velocity
    
    def start_circling(self, target_x, target_y):
        """Start circling around the specified target position."""
        self.state = "circling"
        self.circling_target_x = target_x
        self.circling_target_y = target_y
        
        # Convert to flying bird sprite for circling
        self.sprite = createAnimatedSprite('gfx/birdfly1.png', 16, 16)
        
        # Set initial animation direction
        if self.flying_right:
            self.sprite.select(1)  # Row 1 = flying right
        else:
            self.sprite.select(0)  # Row 0 = flying left
            
        # Set animation speed and start
        self.sprite.speed = 8
        self.sprite.start()
        
        # Set initial position on the circle
        import math
        self.xpos = target_x + math.cos(self.circle_angle) * self.circle_radius
        self.ypos = target_y + math.sin(self.circle_angle) * self.circle_radius
    
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
        # Play bird launch sound
        SFX_BIRD_LAUNCH.play()
        
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
        
        # Play bird explosion sound
        SFX_BIRD_EXPLODING.play()
    
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
        # Play bird launch sound
        SFX_BIRD_LAUNCH.play()
        
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
    
    def _fly_away_randomly(self):
        """Make the bird fly away randomly after sitting for a while."""
        # Play bird launch sound
        SFX_BIRD_LAUNCH.play()
        
        self.state = "scared_flying"
        
        # Choose a random direction to fly away
        self.flying_right = random.choice([True, False])
        
        # Convert to flying bird sprite
        self.sprite = createAnimatedSprite('gfx/birdfly1.png', 16, 16)
        
        # Set animation based on direction
        if self.flying_right:
            self.sprite.select(1)  # Row 1 = flying right
        else:
            self.sprite.select(0)  # Row 0 = flying left
            
        # Set animation speed and start
        self.sprite.speed = 8
        self.sprite.start()