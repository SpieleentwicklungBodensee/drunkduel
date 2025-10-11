import pygame
import ledwall
from base import Screen
from game_state import switchState, tick
from game_state import TILE_WIDTH, TILE_HEIGHT, gameScreen
class GameOverScreen(Screen):
    def draw(self):
        ledwall.centerText('GAME OVER', y=5, color=(255, 0, 0), fontsize=2, align=False)

        if hasattr(gameScreen, 'winner'):
            ledwall.centerText(f'PLAYER {gameScreen.winner}', y=10, color=(0, 255, 0), fontsize=2, align=False)
            ledwall.centerText('WINS!', y=12, color=(0, 255, 0), fontsize=2, align=False)

            ledwall.centerText(f'FINAL SCORE:', y=17, color=(255, 255, 255), align=False)
            ledwall.centerText(f'P1: {gameScreen.players[0].score}  P2: {gameScreen.players[1].score}', y=19, color=(255, 255, 255), align=False)

        if tick % 48 < 24:
            ledwall.centerText('PRESS BUTTON', y=25, color=(255, 255, 0), align=False)
            ledwall.centerText('TO RESTART', y=28, color=(255, 255, 0), align=False)

    def event(self, e):
        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            # Reset game state
            gameScreen.players[0].score = 0
            gameScreen.players[1].score = 0
            gameScreen.players[0].ammo = 4
            gameScreen.players[1].ammo = 4
            gameScreen.players[0].xpos = 2 * TILE_WIDTH
            gameScreen.players[0].ypos = 2 * TILE_HEIGHT
            gameScreen.players[1].xpos = 13 * TILE_WIDTH
            gameScreen.players[1].ypos = 13 * TILE_HEIGHT
            gameScreen.objects.clear()  # Remove all bullets and weapon drops
            gameScreen.weapon_drop_timer = 0  # Reset weapon drop timer
            if hasattr(gameScreen, 'winner'):
                delattr(gameScreen, 'winner')
            switchState('game')