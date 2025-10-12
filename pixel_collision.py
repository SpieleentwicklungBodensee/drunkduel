"""
Pixel-perfect collision detection module for Drunk Duel.
Provides precise collision detection between sprites based on non-transparent pixels.
"""

import pygame
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT

# Override print function
import ledwall
print = ledwall.print

# Cache for loaded sprites and their masks
_sprite_cache = {}
_mask_cache = {}

def get_sprite_surface(tile_type, tile_x=None, tile_y=None):
    """Get the pygame surface for a given tile type."""
    if tile_type == 'o':  # Stone
        cache_key = 'stone'
        if cache_key not in _sprite_cache:
            # Load stone sprite
            _sprite_cache[cache_key] = pygame.image.load('gfx/stone1.png')
        return _sprite_cache[cache_key]
    elif tile_type == '#':  # Fence
        # For fences, we need to get the specific fence type
        if tile_x is not None and tile_y is not None:
            from fence_logic import get_fence_type
            fence_sprite_path = get_fence_type(game_state.level.mapdata, tile_x, tile_y)
            if fence_sprite_path:
                cache_key = f'fence_{fence_sprite_path}'
                if cache_key not in _sprite_cache:
                    _sprite_cache[cache_key] = pygame.image.load(fence_sprite_path)
                return _sprite_cache[cache_key]
        # Fallback to default fence
        cache_key = 'fence_default'
        if cache_key not in _sprite_cache:
            _sprite_cache[cache_key] = pygame.image.load('gfx/fence_top.png')
        return _sprite_cache[cache_key]
    elif tile_type == 'Y':  # Cactus
        cache_key = 'cactus'
        if cache_key not in _sprite_cache:
            _sprite_cache[cache_key] = pygame.image.load('gfx/desert3.png')
        return _sprite_cache[cache_key]
    elif tile_type == 'F':  # Invisible wall - treated as solid for collision
        # Create a solid invisible surface
        cache_key = 'invisible_wall'
        if cache_key not in _sprite_cache:
            surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
            surface.fill((255, 255, 255))  # White, but will be used for mask only
            _sprite_cache[cache_key] = surface
        return _sprite_cache[cache_key]
    
    return None

def get_sprite_mask(tile_type, tile_x=None, tile_y=None):
    """Get or create a collision mask for a sprite."""
    cache_key = f'{tile_type}_{tile_x}_{tile_y}' if tile_x is not None and tile_y is not None else tile_type
    
    if cache_key not in _mask_cache:
        surface = get_sprite_surface(tile_type, tile_x, tile_y)
        if surface:
            # Create mask from non-transparent pixels
            _mask_cache[cache_key] = pygame.mask.from_surface(surface)
        else:
            _mask_cache[cache_key] = None
    
    return _mask_cache[cache_key]

def get_bullet_mask():
    """Get collision mask for bullets."""
    cache_key = 'bullet'
    if cache_key not in _mask_cache:
        # Load bullet sprite
        if hasattr(game_state, 'bullet_sprite') and game_state.bullet_sprite:
            surface = game_state.bullet_sprite.surface
        else:
            surface = pygame.image.load('gfx/bullet.png')
        _mask_cache[cache_key] = pygame.mask.from_surface(surface)
    return _mask_cache[cache_key]

def check_pixel_collision(bullet_x, bullet_y, tile_x, tile_y, tile_type):
    """
    Check for pixel-perfect collision between a bullet and a tile.
    
    Args:
        bullet_x, bullet_y: Bullet position in pixels
        tile_x, tile_y: Tile position in grid coordinates
        tile_type: Type of tile ('o' for stone, '#' for fence, etc.)
    
    Returns:
        True if collision detected, False otherwise
    """
    # Get masks for both objects
    bullet_mask = get_bullet_mask()
    tile_mask = get_sprite_mask(tile_type, tile_x, tile_y)
    
    if not bullet_mask or not tile_mask:
        return False
    
    # Calculate tile position in pixels
    tile_pixel_x = tile_x * TILE_WIDTH
    tile_pixel_y = tile_y * TILE_HEIGHT
    
    # Calculate offset between bullet and tile
    offset_x = int(bullet_x - tile_pixel_x)
    offset_y = int(bullet_y - tile_pixel_y)
    
    # Check for overlap using pygame's mask collision detection
    overlap = tile_mask.overlap(bullet_mask, (offset_x, offset_y))
    
    return overlap is not None

def check_bullet_tile_collision(bullet_x, bullet_y):
    """
    Check if a bullet at the given position collides with any solid tiles.
    
    Args:
        bullet_x, bullet_y: Bullet position in pixels
    
    Returns:
        Tuple of (collision_detected, tile_x, tile_y, tile_type) or (False, None, None, None)
    """
    # Determine which tiles the bullet might be overlapping
    # Check a small area around the bullet position
    bullet_center_x = bullet_x + 4  # Assuming bullet is 8x8 pixels
    bullet_center_y = bullet_y + 4
    
    # Convert to tile coordinates
    center_tile_x = int(bullet_center_x // TILE_WIDTH)
    center_tile_y = int(bullet_center_y // TILE_HEIGHT)
    
    # Check the tile containing the bullet center and adjacent tiles
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            tile_x = center_tile_x + dx
            tile_y = center_tile_y + dy
            
            # Check bounds
            if (0 <= tile_x < game_state.level.getWidth() and 
                0 <= tile_y < game_state.level.getHeight()):
                
                tile_type = game_state.level.getTile(tile_x, tile_y)
                
                # Only check solid tiles
                if tile_type in ['o', '#', 'F', 'Y']:
                    if check_pixel_collision(bullet_x, bullet_y, tile_x, tile_y, tile_type):
                        return True, tile_x, tile_y, tile_type
    
    return False, None, None, None

def clear_cache():
    """Clear the sprite and mask caches to free memory."""
    global _sprite_cache, _mask_cache
    _sprite_cache.clear()
    _mask_cache.clear()
