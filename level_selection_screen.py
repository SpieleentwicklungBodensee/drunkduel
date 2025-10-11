"""
Level selection screen for Drunk Duel.
Allows players to browse and select different levels.
"""

import pygame
import game_state
import controls
from bitmapfont import BitmapFont
from level_loader import get_level_loader

# Override print function
import ledwall
print = ledwall.print



class LevelSelectionScreen:
    """Screen for selecting game levels."""

    def __init__(self):
        self.font = BitmapFont('gfx/wurofont.png', 8, 8)
        self.level_loader = get_level_loader()
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_levels = 8  # How many levels to show at once

    def draw(self):
        """Draw the level selection screen."""
        output = game_state.output

        # Clear screen
        output.fill((20, 20, 40))

        # Title
        title = "SELECT LEVEL"
        title_width = len(title) * 8
        title_x = (game_state.output.get_width() - title_width) // 2
        self.font.drawText(output, title, title_x // 8, 10 // 8, (255, 255, 255))

        # Level count info
        level_count = self.level_loader.get_level_count()
        info_text = f"{level_count} LEVELS AVAILABLE"
        info_width = len(info_text) * 8
        info_x = (game_state.output.get_width() - info_width) // 2
        self.font.drawText(output, info_text, info_x // 8, 25 // 8, (200, 200, 200))

        # Draw level list
        start_y = 45
        levels = self.level_loader.get_level_list()

        # Calculate scroll range
        visible_start = max(0, min(self.selected_index - self.max_visible_levels // 2,
                                  level_count - self.max_visible_levels))
        visible_end = min(level_count, visible_start + self.max_visible_levels)

        for i in range(visible_start, visible_end):
            y_pos = start_y + (i - visible_start) * 12

            level_index, level_name, level_description = levels[i]

            # Highlight selected level
            if i == self.selected_index:
                # Draw selection background
                pygame.draw.rect(output, (60, 60, 100),
                               (10, y_pos - 2, game_state.output.get_width() - 20, 12))
                text_color = (255, 255, 100)
            else:
                text_color = (255, 255, 255)

            # Level name
            self.font.drawText(output, f"{i+1:2d}. {level_name}", 15 // 8, y_pos // 8, text_color)

            # Level description (truncated if too long)
            desc_x = 15 + len(f"{i+1:2d}. {level_name}") * 8 + 10
            max_desc_chars = (game_state.output.get_width() - desc_x - 15) // 8
            if len(level_description) > max_desc_chars:
                truncated_desc = level_description[:max_desc_chars-3] + "..."
            else:
                truncated_desc = level_description

            desc_color = (180, 180, 180) if i != self.selected_index else (200, 200, 150)
            self.font.drawText(output, truncated_desc, desc_x // 8, y_pos // 8, desc_color)

        # Draw level preview if possible
        self._draw_level_preview()

        # Instructions
        instructions = [
            "UP/DOWN: SELECT LEVEL",
            "ENTER/SPACE: CONFIRM",
            "ESC: BACK TO MENU"
        ]

        instruction_start_y = game_state.output.get_height() - len(instructions) * 12 - 10
        for i, instruction in enumerate(instructions):
            inst_width = len(instruction) * 8
            inst_x = (game_state.output.get_width() - inst_width) // 2
            self.font.drawText(output, instruction, inst_x // 8, (instruction_start_y + i * 12) // 8,
                          (150, 150, 150))

    def _draw_level_preview(self):
        """Draw a small preview of the selected level."""
        try:
            current_level = self.level_loader.get_level_by_index(self.selected_index)
            if not current_level:
                return

            # Preview area - positioned at bottom right
            preview_width = 100
            preview_height = 80
            preview_x = game_state.output.get_width() - preview_width - 10
            preview_y = game_state.output.get_height() - preview_height - 40  # Leave space for instructions

            # Background
            pygame.draw.rect(game_state.output, (30, 30, 50),
                           (preview_x, preview_y, preview_width, preview_height))
            pygame.draw.rect(game_state.output, (100, 100, 100),
                           (preview_x, preview_y, preview_width, preview_height), 1)

            # Title
            self.font.drawText(game_state.output, "PREVIEW", (preview_x + 5) // 8, (preview_y - 12) // 8,
                          (200, 200, 200))

            # Calculate scale to fit level in preview
            mapdata = current_level.mapdata
            if not mapdata:
                return

            level_width = len(mapdata[0])
            level_height = len(mapdata)

            scale_x = (preview_width - 10) / level_width
            scale_y = (preview_height - 10) / level_height
            scale = min(scale_x, scale_y, 3)  # Max scale of 3

            # Center the preview
            scaled_width = level_width * scale
            scaled_height = level_height * scale
            offset_x = preview_x + 5 + (preview_width - 10 - scaled_width) // 2
            offset_y = preview_y + 5 + (preview_height - 10 - scaled_height) // 2

            # Draw tiles
            tile_colors = {
                ' ': None,  # Empty space
                '#': (139, 69, 19),    # Brown for fences
                '|': (0, 100, 200),    # Blue for water
                'Y': (255, 255, 0),    # Yellow for desert
                'o': (128, 128, 128),  # Gray for stones
            }

            for y, row in enumerate(mapdata):
                for x, tile in enumerate(row):
                    if tile in tile_colors and tile_colors[tile] is not None:
                        tile_x = offset_x + x * scale
                        tile_y = offset_y + y * scale
                        pygame.draw.rect(game_state.output, tile_colors[tile],
                                       (int(tile_x), int(tile_y), max(1, int(scale)), max(1, int(scale))))

        except Exception as e:
            # If preview fails, just skip it
            pass

    def event(self, event):
        """Handle events for the level selection screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = min(self.level_loader.get_level_count() - 1,
                                        self.selected_index + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select this level and go to game
                self.level_loader.set_current_level(self.selected_index)
                self._reload_current_level()
                game_state.switchState('game')
            elif event.key == pygame.K_ESCAPE:
                # Back to title screen
                game_state.switchState('title')

        # Handle joystick input
        elif event.type == pygame.JOYBUTTONDOWN:
            # Joystick button handling
            if event.button == 0:  # A-Button or similar - confirm selection
                self.level_loader.set_current_level(self.selected_index)
                self._reload_current_level()
                game_state.switchState('game')
            elif event.button == 1:  # B-Button or similar - back to menu
                game_state.switchState('title')
        elif event.type == pygame.JOYHATMOTION:
            # D-Pad navigation
            if event.value[1] == 1:  # Up
                self.selected_index = max(0, self.selected_index - 1)
            elif event.value[1] == -1:  # Down
                self.selected_index = min(self.level_loader.get_level_count() - 1,
                                        self.selected_index + 1)

    def _reload_current_level(self):
        """Reload the game level with the newly selected level data."""
        try:
            from config import load_graphics
            from level import Level

            # Get the tiles (assuming they're already loaded)
            if hasattr(game_state, 'level') and hasattr(game_state.level, 'tiles'):
                tiles = game_state.level.tiles
            else:
                # Fallback: reload graphics
                tiles, _, _, _, _ = load_graphics()

            # Create new level with selected data
            current_level_data = self.level_loader.get_current_level()
            game_state.level = Level(current_level_data.mapdata, tiles)

            print(f"Loaded level: {current_level_data.name}")

        except Exception as e:
            print(f"Error reloading level: {e}")

    def update(self):
        """Update the level selection screen."""
        pass  # Nothing to update for now