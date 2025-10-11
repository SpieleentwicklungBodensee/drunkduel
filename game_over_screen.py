import pygame
import ledwall
import config
from base import Screen
import controls
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState
class GameOverScreen(Screen):
    def draw(self):
        ledwall.centerText('GAME OVER', y=4, color=(255, 0, 0), fontsize=2, align=False)

        if game_state.gameScreen and hasattr(game_state.gameScreen, 'winner'):
            if game_state.tick > 128 or game_state.tick % 32 < 16:
                ledwall.centerText(f'PLAYER {game_state.gameScreen.winner}', y=7, color=(0, 255, 0), fontsize=2, align=False)
                ledwall.centerText('WINS!', color=(0, 255, 0), fontsize=2, align=False)

            ledwall.centerText(f'FINAL SCORE:', y=22, color=(255, 255, 255), align=False)
            ledwall.centerText(f'P1: {game_state.gameScreen.players[0].score}  P2: {game_state.gameScreen.players[1].score}', color=(255, 255, 255), align=False)

        if game_state.tick > 128:
            if game_state.tick % 48 < 24:
                ledwall.centerText('PRESS BUTTON', y=33, color=(255, 255, 0), align=False)
                ledwall.centerText('TO RESTART', y=34, color=(255, 255, 0), align=False)

    def event(self, e):
        if game_state.tick < 128:
            return

        if e.type == pygame.KEYDOWN or e.type == pygame.JOYBUTTONDOWN:
            # Reset game state - only if gameScreen exists
            if game_state.gameScreen:
                game_state.gameScreen.players[0].score = 0
                game_state.gameScreen.players[1].score = 0
                game_state.gameScreen.players[0].ammo = config.INITIAL_AMMO
                game_state.gameScreen.players[1].ammo = config.INITIAL_AMMO
                game_state.gameScreen.players[0].xpos = config.PLAYER_1_STARTX * TILE_WIDTH
                game_state.gameScreen.players[0].ypos = config.PLAYER_1_STARTY * TILE_HEIGHT
                game_state.gameScreen.players[1].xpos = config.PLAYER_2_STARTX * TILE_WIDTH
                game_state.gameScreen.players[1].ypos = config.PLAYER_2_STARTY * TILE_HEIGHT
                game_state.gameScreen.objects.clear()  # Remove all bullets and weapon drops
                game_state.gameScreen.weapon_drop_timer = 0  # Reset weapon drop timer
                game_state.gameScreen.destroyed_cacti.clear()  # Reset cactus respawn timers

                game_state.message = None

                controls.restore(0)
                controls.restore(1)

                # Reset level to original state
                from config import get_level_map_data
                original_mapdata = get_level_map_data()
                game_state.level.mapdata = original_mapdata[:]  # Create a copy

                if hasattr(game_state.gameScreen, 'winner'):
                    delattr(game_state.gameScreen, 'winner')
            switchState('init')
