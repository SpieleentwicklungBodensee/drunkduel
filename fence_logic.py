"""
Fence logic module for Drunk Duel.
Handles intelligent fence placement and connection detection.
"""

from sprite import Sprite

# Override print function
import ledwall
print = ledwall.print


def get_fence_neighbors(mapdata, x, y):
    """
    Get fence neighbors for a position.
    Returns tuple of (top, right, bottom, left) indicating if there's a fence in each direction.
    """
    height = len(mapdata)
    width = len(mapdata[0]) if mapdata else 0
    
    # Check each direction for fence tiles, ensuring we don't go out of bounds
    top = y > 0 and x < len(mapdata[y-1]) and mapdata[y-1][x] == '#'
    right = x < width - 1 and x + 1 < len(mapdata[y]) and mapdata[y][x+1] == '#'
    bottom = y < height - 1 and x < len(mapdata[y+1]) and mapdata[y+1][x] == '#'
    left = x > 0 and mapdata[y][x-1] == '#'
    
    return (top, right, bottom, left)


def get_fence_type(mapdata, x, y):
    """
    Determine the appropriate fence type based on neighbors.
    Returns the fence sprite filename to use.
    """
    if mapdata[y][x] != '#':
        return None
        
    top, right, bottom, left = get_fence_neighbors(mapdata, x, y)
    
    # Count connections
    connections = sum([top, right, bottom, left])
    
    # Get map dimensions for position-based decisions
    map_width = len(mapdata[0]) if mapdata else 0
    is_right_half = x >= map_width // 2
    
    if connections == 0:
        # Isolated fence - use basic fence
        return 'gfx/fence_top.png'
    elif connections == 1:
        # End piece - use fence stubs
        if top:
            return 'gfx/fence_stub_up.png'
        elif right:
            return 'gfx/fence_stub_right.png'
        elif bottom:
            return 'gfx/fence_stub_down.png'
        elif left:
            return 'gfx/fence_stub_left.png'
    elif connections == 2:
        # Either straight line or corner
        if (top and bottom) or (left and right):
            # Straight line
            if top and bottom:
                # Vertical line - choose based on screen position
                if is_right_half:
                    return 'gfx/fence_right.png'  # Right side of screen
                else:
                    return 'gfx/fence_left.png'   # Left side of screen
            else:  # left and right
                return 'gfx/fence_top.png'   # Horizontal line
        else:
            # Corner piece - use appropriate connector
            if top and right:
                return 'gfx/fence_connector_top_right.png'
            elif right and bottom:
                return 'gfx/fence_connector_right_bottom.png'
            elif bottom and left:
                return 'gfx/fence_connector_bottom_left.png'
            elif left and top:
                return 'gfx/fence_connector.png'  # Original: left to top
    elif connections == 3:
        # T-junction - use straight piece for the main direction
        if not top:
            return 'gfx/fence_top.png'     # Horizontal with connection up
        elif not right:
            # Vertical with connection right - choose based on position
            if is_right_half:
                return 'gfx/fence_right.png'
            else:
                return 'gfx/fence_left.png'
        elif not bottom:
            return 'gfx/fence_bottom.png' # Horizontal with connection down
        elif not left:
            # Vertical with connection left - choose based on position
            if is_right_half:
                return 'gfx/fence_right.png'
            else:
                return 'gfx/fence_left.png'
    else:
        # 4-way intersection - use a basic fence piece
        return 'gfx/fence_top.png'
    
    # Fallback
    return 'gfx/fence_top.png'


def create_smart_fence_tiles(mapdata):
    """
    Create a tiles dictionary with smart fence placement.
    Each fence position gets the appropriate fence sprite based on its neighbors.
    """
    tiles = {}
    
    if not mapdata:
        return tiles
        
    height = len(mapdata)
    width = len(mapdata[0]) if mapdata else 0
    
    # Process each position in the map
    for y in range(height):
        for x in range(width):
            if x < len(mapdata[y]) and mapdata[y][x] == '#':
                fence_sprite_path = get_fence_type(mapdata, x, y)
                if fence_sprite_path:
                    # Create a unique key for this position
                    tile_key = f'fence_{x}_{y}'
                    tiles[tile_key] = Sprite(fence_sprite_path)
    
    return tiles


def get_fence_tile_for_position(mapdata, x, y):
    """
    Get the appropriate fence tile sprite for a specific position.
    Returns the sprite or None if not a fence position.
    """
    if not mapdata or y >= len(mapdata) or x >= len(mapdata[y]) or mapdata[y][x] != '#':
        return None
        
    fence_sprite_path = get_fence_type(mapdata, x, y)
    if fence_sprite_path:
        return Sprite(fence_sprite_path)
    
    return None