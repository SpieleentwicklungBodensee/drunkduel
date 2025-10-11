"""
Level management module for Drunk Duel.
Contains the Level class and level-related functionality.
"""

from game_state import TILE_WIDTH, TILE_HEIGHT

# Override print function
import ledwall
print = ledwall.print


def process_water_tiles(mapdata):
    """
    Process map data to convert || patterns to <> patterns for animated water.
    Returns a new mapdata with water sides properly set.
    """
    if not mapdata:
        return mapdata
    
    processed_mapdata = []
    
    for row in mapdata:
        new_row = ""
        i = 0
        while i < len(row):
            if i < len(row) - 1 and row[i] == '|' and row[i + 1] == '|':
                # Found || pattern, replace with <>
                new_row += '<>'
                i += 2
            else:
                new_row += row[i]
                i += 1
        processed_mapdata.append(new_row)
    
    return processed_mapdata


class Level:
    """Represents a game level with tile-based map data."""

    def __init__(self, mapdata, tiles):
        # Process water tiles before storing
        self.mapdata = process_water_tiles(mapdata)
        self.tiles = tiles

        self.width = len(self.mapdata[0])
        self.height = len(self.mapdata)

    def setTile(self, x, y, tile):
        """Set a tile at the given coordinates."""
        self.mapdata[y] = self.mapdata[y][:x] + tile + self.mapdata[y][x+1:]

    def getTile(self, x, y):
        """Get the tile at the given coordinates."""
        return self.mapdata[int(y)][int(x)]

    def getWidth(self):
        """Get the width of the level in tiles."""
        return self.width

    def getHeight(self):
        """Get the height of the level in tiles."""
        return self.height

    def draw(self, output):
        """Draw the level to the output surface."""
        for y in range(self.height):
            for x in range(self.width):
                tile = self.getTile(x, y)
                if tile in self.tiles and self.tiles[tile] is not None:
                    self.tiles[tile].draw(output, x * TILE_WIDTH, y * TILE_HEIGHT)