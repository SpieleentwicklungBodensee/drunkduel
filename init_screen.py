import pygame
import ledwall
import ledwall
from base import Screen
from game_state import switchState

from level_loader import get_level_loader

# Override print function
print = ledwall.print



class InitScreen(Screen):
    def draw(self):
        # Display current level information
        level_loader = get_level_loader()
        current_level = level_loader.get_current_level()
        
        if current_level:
            ledwall.centerText('LEVEL SELECTED:', y=5, color=(255, 255, 255), align=False)
            ledwall.centerText(current_level.name.upper(), y=8, color=(255, 255, 0), fontsize=2, align=False)
            
            # Show level description if available
            description = getattr(current_level, 'description', '') or ''
            if description and description.strip():
                ledwall.centerText(description.upper(), y=12, color=(200, 200, 200), align=False)
        else:
            ledwall.centerText('NO LEVEL SELECTED', y=8, color=(255, 100, 100), align=False)
        
        # Instructions
        ledwall.centerText('PRESS ANY KEY TO START', y=20, color=(0, 255, 0), align=False)
        ledwall.centerText('GAME WITH THIS LEVEL', y=22, color=(0, 255, 0), align=False)

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            switchState('title')