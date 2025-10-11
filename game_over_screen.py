import pygame
import ledwall
from base import Screen
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState
class GameOverScreen(Screen):
    def draw(self):
        ledwall.centerText('GAME OVER', y=5, color=(255, 0, 0), fontsize=2, align=False)

        if game_state.gameScreen and hasattr(game_state.gameScreen, 'winner'):
            ledwall.centerText(f'PLAYER {game_state.gameScreen.winner}', y=10, color=(0, 255, 0), fontsize=2, align=False)
            ledwall.centerText('WINS!', y=12, color=(0, 255, 0), fontsize=2, align=False)

            ledwall.centerText(f'FINAL SCORE:', y=17, color=(255, 255, 255), align=False)
            ledwall.centerText(f'P1: {game_state.gameScreen.players[0].score}  P2: {game_state.gameScreen.players[1].score}', y=19, color=(255, 255, 255), align=False)

        if game_state.tick % 48 < 24:
            ledwall.centerText('PRESS BUTTON', y=30, color=(255, 255, 0), align=False)
            ledwall.centerText('TO RESTART', y=36, color=(255, 255, 0), align=False)

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            # Reset game state - only if gameScreen exists
            if game_state.gameScreen:
                game_state.gameScreen.players[0].score = 0
                game_state.gameScreen.players[1].score = 0
                game_state.gameScreen.players[0].ammo = 4
                game_state.gameScreen.players[1].ammo = 4
                game_state.gameScreen.players[0].xpos = 2 * TILE_WIDTH
                game_state.gameScreen.players[0].ypos = 2 * TILE_HEIGHT
                game_state.gameScreen.players[1].xpos = 13 * TILE_WIDTH
                game_state.gameScreen.players[1].ypos = 13 * TILE_HEIGHT
                game_state.gameScreen.objects.clear()  # Remove all bullets and weapon drops
                game_state.gameScreen.weapon_drop_timer = 0  # Reset weapon drop timer
                if hasattr(game_state.gameScreen, 'winner'):
                    delattr(game_state.gameScreen, 'winner')
            switchState('game')