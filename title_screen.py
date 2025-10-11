import pygame
import ledwall
import config
import controls
import random
from base import Screen
import game_state
from sound_manager import SFX_BORING

# Override print function
import ledwall
print = ledwall.print


class TitleScreen(Screen):
    def __init__(self):
        self.selected_option = 0  # 0 = Mit Alkohol, 1 = Alkoholfrei, 2 = Level Auswahl
        self.show_menu = False
        self.blink_timer = 0

    def draw(self):
        ledwall.centerText('DRUNK', y=2, color=(0, 255, 0), fontsize=3, align=False)
        ledwall.centerText('DUEL', y=3, color=(0, 255, 0), fontsize=3, align=False)

        ledwall.centerText('BODENSEE', y=15, color=(255, 255, 255), align=False)
        ledwall.centerText('GAMEJAM', align=False)
        ledwall.centerText('2025', align=False)

        if not self.show_menu:
            if game_state.tick % 48 < 24:
                ledwall.centerText('PRESS BUTTON', y=25, color=(255, 255, 0), align=False)
        else:
            # Zeige Menü-Optionen
            ledwall.centerText('SPIEL-OPTIONEN:', y=20, color=(255, 255, 255), align=False)

            # Option 1: Mit Alkohol
            color1 = (255, 255, 0) if self.selected_option == 0 else (128, 128, 128)
            if self.selected_option == 0 and game_state.tick % 30 < 15:
                # Add shake effect for "MIT ALKOHOL" when selected
                shake_x = random.randint(-1, 1)
                shake_y = random.randint(-1, 1)
                
                # Calculate center position manually and add shake offset
                text = '> MIT ALKOHOL <'
                screen_chars_width = ledwall.SCR_W // 8  # Assuming 8-pixel character width
                center_x = (screen_chars_width - len(text)) // 2 + shake_x
                
                # Draw the text
                ledwall.drawText(text, x=center_x, y=22 + shake_y, color=color1, align=False)
                
                # Add puke animation around the text
                from puke_effect import PukeEffect
                PukeEffect.draw_around_text(center_x, 22 + shake_y, len(text))
            else:
                text = 'MIT ALKOHOL' if self.selected_option != 0 else '> MIT ALKOHOL <'
                if self.selected_option == 0:
                    # Still shake even when not blinking
                    shake_x = random.randint(-1, 1) 
                    shake_y = random.randint(-1, 1)
                    screen_chars_width = ledwall.SCR_W // 8
                    center_x = (screen_chars_width - len(text)) // 2 + shake_x
                    
                    # Draw the text
                    ledwall.drawText(text, x=center_x, y=22 + shake_y, color=color1, align=False)
                    
                    # Add puke animation around the text
                    from puke_effect import PukeEffect
                    PukeEffect.draw_around_text(center_x, 22 + shake_y, len(text))
                else:
                    ledwall.centerText('MIT ALKOHOL', y=22, color=color1, align=False)

            # Option 2: Alkoholfrei
            color2 = (255, 255, 0) if self.selected_option == 1 else (128, 128, 128)
            if self.selected_option == 1 and game_state.tick % 30 < 15:
                ledwall.centerText('> ALKOHOLFREI <', y=24, color=color2, align=False)
            else:
                ledwall.centerText('ALKOHOLFREI', y=24, color=color2, align=False)

            # Option 3: Level Auswahl
            color3 = (255, 255, 0) if self.selected_option == 2 else (128, 128, 128)
            if self.selected_option == 2 and game_state.tick % 30 < 15:
                ledwall.centerText('> LEVEL WAEHLEN <', y=26, color=color3, align=False)
            else:
                ledwall.centerText('LEVEL WAEHLEN', y=26, color=color3, align=False)

            ledwall.centerText('ENTER ZUM STARTEN', y=29, color=(0, 255, 0), align=False)

    def event(self, e):
        if not self.show_menu:
            # Erste Eingabe zeigt das Menü
            if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
                self.show_menu = True
        else:
            # Navigation im Menü
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP or e.key == pygame.K_w:
                    self.selected_option = max(0, self.selected_option - 1)
                elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
                    self.selected_option = min(2, self.selected_option + 1)
                elif e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                    self._handle_selection()
            elif e.type == pygame.JOYBUTTONDOWN:
                # Joystick Button wechselt zwischen Optionen oder startet
                if e.button == 0:  # A-Button oder ähnlich
                    self._handle_selection()
                else:
                    self.selected_option = (self.selected_option + 1) % 3  # Cycle through options
            elif e.type in (pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
                actions = controls.handleJoyEvent(e)
                for action in actions:
                    if action == 'moveup':
                        self.selected_option = max(0, self.selected_option - 1)
                    elif action == 'movedown':
                        self.selected_option = min(2, self.selected_option + 1)

    def _handle_selection(self):
        """Behandelt die Auswahl im Menü."""
        if self.selected_option == 0:
            # Mit Alkohol spielen
            config.ALCOHOL_ENABLED = True
            game_state.switchState('game')
        elif self.selected_option == 1:
            # Alkoholfrei spielen
            config.ALCOHOL_ENABLED = False
            SFX_BORING.play()
            game_state.switchState('game')
        elif self.selected_option == 2:
            # Level-Auswahl öffnen
            game_state.switchState('levels')

    def _start_game(self):
        """Startet das Spiel mit der gewählten Alkohol-Einstellung (Legacy-Methode)."""
        config.ALCOHOL_ENABLED = (self.selected_option == 0)
        if not config.ALCOHOL_ENABLED:
            SFX_BORING.play()
        game_state.switchState('game')