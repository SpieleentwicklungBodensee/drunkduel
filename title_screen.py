import pygame
import ledwall
import config
import controls
import random
from base import Screen
import game_state
from sound_manager import SFX_BORING
from player import load_player_sprites

# Override print function
import ledwall
print = ledwall.print

MODE_NORMAL = 0
MODE_ALCOHOL = 1
MODE_LEVELSELECT = 2

class TitleScreen(Screen):
    def __init__(self):
        self.selected_option = MODE_NORMAL
        self.show_menu = False
        self.blink_timer = 0

        # Load player sprites for menu decoration
        self.player1_sprite, self.player2_sprite = load_player_sprites()

        # Set up left player (facing right, walking animation)
        self.left_player_x = 8   # Left side of screen
        self.left_player_y = 140  # Middle height
        self.player1_sprite.select(controls.DIR_RIGHT)  # Face right
        self.player1_sprite.speed = 15  # Slower animation
        self.player1_sprite.start()

        # Set up right player (facing left, walking animation)
        self.right_player_x = ledwall.SCR_W - 24  # Right side of screen
        self.right_player_y = 140  # Middle height
        self.player2_sprite.select(controls.DIR_LEFT)  # Face left
        self.player2_sprite.speed = 15  # Slower animation
        self.player2_sprite.start()

    def draw(self):
        # Draw animated players on sides of screen
        self.player1_sprite.draw(game_state.output, self.left_player_x, self.left_player_y)
        self.player2_sprite.draw(game_state.output, self.right_player_x, self.right_player_y)

        ledwall.centerText('DRUNK', y=2, color=(0, 255, 0), fontsize=3, align=False)
        ledwall.centerText('~DUEL~', y=3, color=(0, 255, 0), fontsize=3, align=False)

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
            color1 = (255, 255, 0) if self.selected_option == MODE_ALCOHOL else (128, 128, 128)
            if self.selected_option == MODE_ALCOHOL and game_state.tick % 30 < 15:
                # Add shake effect for "MIT ALKOHOL" when selected
                shake_x = random.randint(-1, 1)
                shake_y = random.randint(-1, 1)

                # Calculate center position manually and add shake offset
                text = '> MIT ALKOHOL <'
                screen_chars_width = ledwall.SCR_W // 8  # Assuming 8-pixel character width
                center_x = (screen_chars_width - len(text)) // 2 + shake_x

                # Draw the text
                ledwall.drawText(text, x=center_x, y=24 + shake_y, color=color1, align=False)

                # Add puke animation around the text
                from puke_effect import PukeEffect
                PukeEffect.draw_around_text(center_x, 24 + shake_y, len(text))
            else:
                text = 'MIT ALKOHOL' if self.selected_option != MODE_ALCOHOL else '> MIT ALKOHOL <'
                if self.selected_option == MODE_ALCOHOL:
                    # Still shake even when not blinking
                    shake_x = random.randint(-1, 1)
                    shake_y = random.randint(-1, 1)
                    screen_chars_width = ledwall.SCR_W // 8
                    center_x = (screen_chars_width - len(text)) // 2 + shake_x

                    # Draw the text
                    ledwall.drawText(text, x=center_x, y=24 + shake_y, color=color1, align=False)

                    # Add puke animation around the text
                    from puke_effect import PukeEffect
                    PukeEffect.draw_around_text(center_x, 24 + shake_y, len(text))
                else:
                    ledwall.centerText('MIT ALKOHOL', y=24, color=color1, align=False)

            # Option 2: Alkoholfrei
            color2 = (255, 255, 0) if self.selected_option == MODE_NORMAL else (128, 128, 128)
            if self.selected_option == MODE_NORMAL and game_state.tick % 30 < 15:
                ledwall.centerText('> ALKOHOLFREI <', y=22, color=color2, align=False)
            else:
                ledwall.centerText('ALKOHOLFREI', y=22, color=color2, align=False)

            # Option 3: Level Auswahl
            color3 = (255, 255, 0) if self.selected_option == MODE_LEVELSELECT else (128, 128, 128)
            if self.selected_option == MODE_LEVELSELECT and game_state.tick % 30 < 15:
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
        if self.selected_option == MODE_ALCOHOL:
            # Mit Alkohol spielen
            config.ALCOHOL_ENABLED = True
            game_state.switchState('game')
        elif self.selected_option == MODE_NORMAL:
            # Alkoholfrei spielen
            config.ALCOHOL_ENABLED = False
            if config.PLAY_BORING_SOUND:
                SFX_BORING.play()
            game_state.switchState('game')
        elif self.selected_option == MODE_LEVELSELECT:
            # Level-Auswahl öffnen
            game_state.switchState('levels')

    def _start_game(self):
        """Startet das Spiel mit der gewählten Alkohol-Einstellung (Legacy-Methode)."""
        config.ALCOHOL_ENABLED = (self.selected_option == MODE_ALCOHOL)
        if not config.ALCOHOL_ENABLED:
            SFX_BORING.play()
        game_state.switchState('game')

    def update(self):
        """Update the title screen animations."""
        if not self.show_menu:
            return

        # Change player behavior based on selected option
        if self.selected_option == MODE_ALCOHOL:  # MIT ALKOHOL selected
            # Make players "drunk" - wobble and occasional puke
            wobble_x = random.randint(-1, 1)
            wobble_y = random.randint(-1, 1)

            # Apply wobble but keep players on screen
            self.left_player_x = max(0, min(8 + wobble_x, 20))
            self.left_player_y = max(100, min(140 + wobble_y, 180))

            self.right_player_x = max(ledwall.SCR_W - 44, min(ledwall.SCR_W - 24 + wobble_x, ledwall.SCR_W - 16))
            self.right_player_y = max(100, min(140 + wobble_y, 180))

            # Occasionally make players "throw up" when alcohol is selected
            if random.randint(1, 180) == 1:  # About once every 3 seconds at 60fps
                from puke_effect import PukeEffect
                # Left player puke (facing right, so puke goes right)
                PukeEffect.draw_at_position(game_state.output, self.left_player_x + 16, self.left_player_y + 8, particle_count=4)
                # Right player puke (facing left, so puke goes left)
                PukeEffect.draw_at_position(game_state.output, self.right_player_x - 8, self.right_player_y + 8, particle_count=4)

        elif self.selected_option == MODE_NORMAL:  # ALKOHOLFREI selected
            # Players walk normally but without any drunk effects
            self.left_player_x = 8
            self.left_player_y = 140
            self.right_player_x = ledwall.SCR_W - 24
            self.right_player_y = 140

            # Keep walking animations running (but steady, no wobble)
            if not self.player1_sprite.running:
                self.player1_sprite.select(controls.DIR_RIGHT)
                self.player1_sprite.start()
            if not self.player2_sprite.running:
                self.player2_sprite.select(controls.DIR_LEFT)
                self.player2_sprite.start()

        elif self.selected_option == MODE_LEVELSELECT:  # LEVEL WAEHLEN selected
            # Players look around (change facing direction occasionally)
            if random.randint(1, 120) == 1:  # Change direction every 2 seconds
                # Left player looks around
                new_dir = random.choice([controls.DIR_UP, controls.DIR_DOWN, controls.DIR_RIGHT])
                self.player1_sprite.select(new_dir)
                self.player1_sprite.start()

                # Right player looks around
                new_dir = random.choice([controls.DIR_UP, controls.DIR_DOWN, controls.DIR_LEFT])
                self.player2_sprite.select(new_dir)
                self.player2_sprite.start()

            # Reset to normal positions
            self.left_player_x = 8
            self.left_player_y = 140
            self.right_player_x = ledwall.SCR_W - 24
            self.right_player_y = 140

        # Default case: reset animations if they were stopped
        if self.selected_option != MODE_NORMAL:  # Not alkoholfrei
            if not self.player1_sprite.running:
                self.player1_sprite.select(controls.DIR_RIGHT)
                self.player1_sprite.start()
            if not self.player2_sprite.running:
                self.player2_sprite.select(controls.DIR_LEFT)
                self.player2_sprite.start()