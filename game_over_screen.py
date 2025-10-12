import pygame
import ledwall
import config
from base import Screen
from message import Message
import controls
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState
class GameOverScreen(Screen):
    def __init__(self):
        super().__init__()

        # won't be displayed, only for voice
        self.speechMessage = Message(0, 0, ['', '', 'spieler', ['eins', 'zwei'][game_state.gameScreen.winner], 'wins'], (0, 0, 0), 0)

    def draw(self):
        ledwall.centerText('GAME OVER', y=4, color=(255, 0, 0), fontsize=2, align=False)

        if game_state.gameScreen and hasattr(game_state.gameScreen, 'winner'):
            if game_state.tick > 128 or game_state.tick % 32 < 16:
                ledwall.centerText(f'PLAYER {game_state.gameScreen.winner + 1}', y=7, color=(0, 255, 0), fontsize=2, align=False)
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
            switchState('title')

    def update(self):
        self.speechMessage.update()
