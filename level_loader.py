"""
Level loader module for Drunk Duel.
Handles loading levels from files and managing level collections.
"""

import os
import json
import glob
from typing import List, Dict, Tuple, Optional

# Override print function
import ledwall
print = ledwall.print



class LevelData:
    """Represents a single level's data and metadata."""

    def __init__(self, name: str, mapdata: List[str], metadata: Dict = None):
        self.name = name
        self.mapdata = mapdata
        self.metadata = metadata or {}

    @property
    def width(self) -> int:
        """Get the width of the level in tiles."""
        return len(self.mapdata[0]) if self.mapdata else 0

    @property
    def height(self) -> int:
        """Get the height of the level in tiles."""
        return len(self.mapdata)

    @property
    def description(self) -> str:
        """Get the level description."""
        return self.metadata.get('description', 'No description')

    @property
    def author(self) -> str:
        """Get the level author."""
        return self.metadata.get('author', 'Unknown')

    @property
    def difficulty(self) -> str:
        """Get the level difficulty."""
        return self.metadata.get('difficulty', 'Normal')


class LevelLoader:
    """Manages loading and access to game levels."""

    def __init__(self, levels_directory: str = "levels"):
        self.levels_directory = levels_directory
        self.levels: List[LevelData] = []
        self.current_level_index = 0

        # Ensure levels directory exists
        if not os.path.exists(levels_directory):
            os.makedirs(levels_directory)

    def load_all_levels(self) -> None:
        """Load all levels from the levels directory."""
        self.levels.clear()

        # Load .json level files
        json_files = glob.glob(os.path.join(self.levels_directory, "*.json"))
        for filepath in sorted(json_files):
            level_data = self._load_json_level(filepath)
            if level_data:
                self.levels.append(level_data)

        # Load .txt level files (simple format)
        txt_files = glob.glob(os.path.join(self.levels_directory, "*.txt"))
        for filepath in sorted(txt_files):
            level_data = self._load_txt_level(filepath)
            if level_data:
                self.levels.append(level_data)

        # If no levels found, create default level
        if not self.levels:
            self._create_default_level()

        print(f"Loaded {len(self.levels)} levels")

    def _load_json_level(self, filepath: str) -> Optional[LevelData]:
        """Load a level from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            name = data.get('name', os.path.splitext(os.path.basename(filepath))[0])
            mapdata = data.get('mapdata', [])
            metadata = data.get('metadata', {})

            # Validate mapdata
            if not mapdata or not isinstance(mapdata, list):
                print(f"Invalid mapdata in {filepath}")
                return None

            # Ensure all rows have the same length
            if mapdata:
                max_width = max(len(row) for row in mapdata)
                mapdata = [row.ljust(max_width) for row in mapdata]

            return LevelData(name, mapdata, metadata)

        except Exception as e:
            print(f"Error loading level from {filepath}: {e}")
            return None

    def _load_txt_level(self, filepath: str) -> Optional[LevelData]:
        """Load a level from a simple text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Remove newlines and empty lines
            mapdata = [line.rstrip('\n\r') for line in lines if line.strip()]

            if not mapdata:
                print(f"Empty level file: {filepath}")
                return None

            # Ensure all rows have the same length
            max_width = max(len(row) for row in mapdata)
            mapdata = [row.ljust(max_width) for row in mapdata]

            name = os.path.splitext(os.path.basename(filepath))[0]

            return LevelData(name, mapdata)

        except Exception as e:
            print(f"Error loading level from {filepath}: {e}")
            return None

    def _create_default_level(self) -> None:
        """Create the default hardcoded level if no levels are found."""
        default_mapdata = [
            '       ||       ',
            '       ||   Y   ',
            '    Y  ||     o ',
            '       ||       ',
            '       || Y     ',
            '   o   ||       ',
            '      Y||  o    ',
            '       ||    Y  ',
            '  Y    ||       ',
            '   o   ||       ',
            '       ||       ',
            '       ||     o ',
            '     Y ||       ',
            '  o    ||  Y    ',
            '       ||       ',
            '#######||#######',
        ]

        metadata = {
            'description': 'Classic Drunk Duel arena',
            'author': 'SpieleentwicklungBodensee',
            'difficulty': 'Normal'
        }

        default_level = LevelData("Classic", default_mapdata, metadata)
        self.levels.append(default_level)

    def get_current_level(self) -> LevelData:
        """Get the currently selected level."""
        if not self.levels:
            self._create_default_level()
        return self.levels[self.current_level_index]

    def get_level_by_name(self, name: str) -> Optional[LevelData]:
        """Get a level by its name."""
        for level in self.levels:
            if level.name.lower() == name.lower():
                return level
        return None

    def get_level_by_index(self, index: int) -> Optional[LevelData]:
        """Get a level by its index."""
        if 0 <= index < len(self.levels):
            return self.levels[index]
        return None

    def next_level(self) -> LevelData:
        """Switch to the next level."""
        if self.levels:
            self.current_level_index = (self.current_level_index + 1) % len(self.levels)
        return self.get_current_level()

    def previous_level(self) -> LevelData:
        """Switch to the previous level."""
        if self.levels:
            self.current_level_index = (self.current_level_index - 1) % len(self.levels)
        return self.get_current_level()

    def set_current_level(self, index: int) -> bool:
        """Set the current level by index. Returns True if successful."""
        if 0 <= index < len(self.levels):
            self.current_level_index = index
            return True
        return False

    def get_level_count(self) -> int:
        """Get the total number of levels."""
        return len(self.levels)

    def get_level_list(self) -> List[Tuple[int, str, str]]:
        """Get a list of (index, name, description) for all levels."""
        return [(i, level.name, level.description) for i, level in enumerate(self.levels)]

    def save_level(self, level_data: LevelData, filename: str = None) -> bool:
        """Save a level to a JSON file."""
        if filename is None:
            filename = f"{level_data.name.lower().replace(' ', '_')}.json"

        filepath = os.path.join(self.levels_directory, filename)

        try:
            data = {
                'name': level_data.name,
                'mapdata': level_data.mapdata,
                'metadata': level_data.metadata
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Level saved to {filepath}")
            return True

        except Exception as e:
            print(f"Error saving level to {filepath}: {e}")
            return False


# Global level loader instance
level_loader = LevelLoader()


def initialize_levels():
    """Initialize the level loading system."""
    level_loader.load_all_levels()


def get_current_level_data():
    """Get the current level's map data (for backward compatibility)."""
    return level_loader.get_current_level().mapdata


def get_level_loader():
    """Get the global level loader instance."""
    return level_loader