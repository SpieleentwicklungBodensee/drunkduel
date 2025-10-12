import pygame
import ledwall
import config
from base import Screen
from message import Message
import controls
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState
from sound_manager import SFX_GAME_OVER_GUITAR
class GameOverScreen(Screen):
    def __init__(self):
        super().__init__()

        # won't be displayed, only for voice
        if getattr(config, 'SINGLEPLAYER_MODE', False):
            # Check if this is a Duck Hunt game over (player died) or victory
            if getattr(config, 'DUCK_HUNT_MODE', False) and hasattr(game_state.gameScreen, 'winner') and game_state.gameScreen.winner == -1:
                self.speechMessage = Message(0, 0, ['', '', 'game', 'over'], (0, 0, 0), 0)
            else:
                self.speechMessage = Message(0, 0, ['', '', 'mission', 'complete'], (0, 0, 0), 0)
        else:
            self.speechMessage = Message(0, 0, ['', '', 'spieler', ['eins', 'zwei'][game_state.gameScreen.winner], 'wins'], (0, 0, 0), 0)
        
        SFX_GAME_OVER_GUITAR.play()
    def draw(self):
        if getattr(config, 'SINGLEPLAYER_MODE', False):
            # Check if this is Duck Hunt mode death or normal single-player victory
            if getattr(config, 'DUCK_HUNT_MODE', False) and hasattr(game_state.gameScreen, 'winner') and game_state.gameScreen.winner == -1:
                # Duck Hunt game over (player died)
                ledwall.centerText('GAME OVER', y=4, color=(255, 0, 0), fontsize=2, align=False)
                
                if game_state.tick > 128 or game_state.tick % 32 < 16:
                    ledwall.centerText('HUNTER DOWN!', y=7, color=(255, 255, 0), align=False)
                
                ledwall.centerText(f'BIRDS SHOT: {game_state.gameScreen.bird_score}', y=20, color=(255, 255, 255), align=False)
                if hasattr(game_state.gameScreen.players[0], 'score'):
                    ledwall.centerText(f'FINAL SCORE: {game_state.gameScreen.players[0].score}', y=21, color=(255, 255, 255), align=False)
            elif getattr(config, 'DUCK_HUNT_MODE', False):
                # Duck Hunt all levels completed
                ledwall.centerText('ALL LEVELS', y=4, color=(0, 255, 0), fontsize=2, align=False)
                ledwall.centerText('CLEARED!', y=6, color=(0, 255, 0), fontsize=2, align=False)

                if game_state.tick > 128 or game_state.tick % 32 < 16:
                    ledwall.centerText('MASTER HUNTER!', y=17, color=(255, 255, 0), align=False)

                # Show total birds shot across all levels
                ledwall.centerText(f'TOTAL BIRDS: {game_state.gameScreen.bird_score}', y=20, color=(255, 255, 255), align=False)
                
                # Show level completed
                from level_loader import get_level_loader
                level_loader = get_level_loader()
                total_levels = level_loader.get_level_count()
                ledwall.centerText(f'LEVELS: {total_levels}/{total_levels}', y=22, color=(255, 255, 255), align=False)
            else:
                # Normal single-player victory screen
                ledwall.centerText('MISSION', y=4, color=(255, 0, 0), fontsize=2, align=False)
                ledwall.centerText('COMPLETE!', y=6, color=(255, 0, 0), fontsize=2, align=False)

                if game_state.tick > 128 or game_state.tick % 32 < 16:
                    ledwall.centerText('ALL BIRDS', y=17, color=(0, 255, 0), align=False)
                    ledwall.centerText('ELIMINATED!', y=18, color=(0, 255, 0), align=False)

                ledwall.centerText(f'BIRDS SHOT: {game_state.gameScreen.bird_score}', y=20, color=(255, 255, 255), align=False)
        else:
            # Multiplayer mode victory screen  
            ledwall.centerText('GAME OVER', y=4, color=(255, 0, 0), fontsize=2, align=False)

            if game_state.gameScreen and hasattr(game_state.gameScreen, 'winner'):
                if game_state.tick > 128 or game_state.tick % 32 < 16:
                    ledwall.centerText(f'PLAYER {game_state.gameScreen.winner + 1}', y=7, color=(0, 255, 0), fontsize=2, align=False)
                    ledwall.centerText('WINS!', color=(0, 255, 0), fontsize=2, align=False)

                ledwall.centerText(f'FINAL SCORE:', y=22, color=(255, 255, 255), align=False)
                if len(game_state.gameScreen.players) > 1:
                    ledwall.centerText(f'P1: {game_state.gameScreen.players[0].score}  P2: {game_state.gameScreen.players[1].score}', color=(255, 255, 255), align=False)
                else:
                    ledwall.centerText(f'P1: {game_state.gameScreen.players[0].score}', color=(255, 255, 255), align=False)

        if game_state.tick > 128:
            if game_state.tick % 48 < 24:
                ledwall.centerText('PRESS BUTTON', y=33, color=(255, 255, 0), align=False)
                ledwall.centerText('TO RESTART', y=34, color=(255, 255, 0), align=False)

    def event(self, e):
        if game_state.tick < 128:
            return

        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            switchState('title')

    def update(self):
        self.speechMessage.update()
