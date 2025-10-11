"""
Puke effect helper module for Drunk Duel.
Contains reusable puke animation effects.
"""

import random
import ledwall
import game_state


class PukeEffect:
    """Static helper class for drawing puke/vomit effects."""
    
    # Puke colors (green/yellow variations)
    PUKE_COLORS = [(0, 255, 0), (255, 255, 0), (128, 255, 0), (200, 255, 0)]
    
    @staticmethod
    def draw_around_player(output, player_x, player_y, face_direction):
        """
        Draw puke effect around a player based on their facing direction.
        
        Args:
            output: The surface to draw on
            player_x: Player's X position in pixels
            player_y: Player's Y position in pixels
            face_direction: Player's facing direction (from controls module)
        """
        import controls
        
        # Calculate position in front of player based on facing direction
        if face_direction == controls.DIR_LEFT:
            vomit_x = player_x - 8
            vomit_y = player_y + 8
        elif face_direction == controls.DIR_RIGHT:
            vomit_x = player_x + 16
            vomit_y = player_y + 8
        elif face_direction == controls.DIR_UP:
            vomit_x = player_x + 8
            vomit_y = player_y - 8
        else:  # DIR_DOWN
            vomit_x = player_x + 8
            vomit_y = player_y + 16
        
        # Draw puke particles
        PukeEffect._draw_particles(output, vomit_x, vomit_y, particle_count=3)
    
    @staticmethod
    def draw_around_text(text_x_chars, text_y_chars, text_length_chars, particle_count=6):
        """
        Draw puke effect around text.
        
        Args:
            text_x_chars: Text X position in character coordinates
            text_y_chars: Text Y position in character coordinates  
            text_length_chars: Text length in characters
            particle_count: Number of particles to draw (default: 6)
        """
        # Convert character coordinates to pixel coordinates
        pixel_x = text_x_chars * 8  # 8 pixels per character
        pixel_y = text_y_chars * 8  # 8 pixels per character
        text_width = text_length_chars * 8
        text_height = 8
        
        # Draw particles around the text
        for i in range(particle_count):
            # Random position around the text
            if i < particle_count // 2:
                # Particles on the left side of text
                base_x = pixel_x - 8
                base_y = pixel_y + random.randint(0, text_height)
            else:
                # Particles on the right side of text
                base_x = pixel_x + text_width + 4
                base_y = pixel_y + random.randint(0, text_height)
            
            # Add random offsets
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-2, 2)
            
            final_x = base_x + offset_x
            final_y = base_y + offset_y
            
            # Draw the particle
            PukeEffect._draw_single_particle(game_state.output, final_x, final_y)
    
    @staticmethod
    def draw_at_position(output, x, y, particle_count=3, spread=4):
        """
        Draw puke effect at a specific position.
        
        Args:
            output: The surface to draw on
            x: X position in pixels
            y: Y position in pixels
            particle_count: Number of particles to draw (default: 3)
            spread: Maximum offset from center position (default: 4)
        """
        PukeEffect._draw_particles(output, x, y, particle_count, spread)
    
    @staticmethod
    def _draw_particles(output, center_x, center_y, particle_count=3, spread=4):
        """
        Draw multiple puke particles around a center position.
        
        Args:
            output: The surface to draw on
            center_x: Center X position in pixels
            center_y: Center Y position in pixels
            particle_count: Number of particles to draw
            spread: Maximum offset from center position
        """
        for i in range(particle_count):
            # Random offsets from center
            offset_x = random.randint(-spread, spread)
            offset_y = random.randint(-2, 2)  # Less vertical spread
            
            final_x = center_x + offset_x
            final_y = center_y + offset_y
            
            PukeEffect._draw_single_particle(output, final_x, final_y)
    
    @staticmethod
    def _draw_single_particle(output, x, y):
        """
        Draw a single puke particle at the specified position.
        
        Args:
            output: The surface to draw on
            x: X position in pixels
            y: Y position in pixels
        """
        # Check bounds
        if 0 <= x < ledwall.SCR_W and 0 <= y < ledwall.SCR_H:
            try:
                color = random.choice(PukeEffect.PUKE_COLORS)
                output.set_at((int(x), int(y)), color)
            except:
                pass  # Ignore errors if outside screen bounds