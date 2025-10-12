"""
Game state management module.
Contains global game state variables and state switching logic.
"""

import controls
import config

# Override print function
import ledwall
print = ledwall.print


# Global game state variables
tick = 0
currentScreen = None
BRIGHTNESS = 0
clock = None

# Game objects that screens need access to
gameScreen = None
initScreen = None
titleScreen = None
gameOverScreen = None
levelSelectionScreen = None
confirmScreen = None
level = None
output = None
message = None

# Constants
TILE_WIDTH = 16
TILE_HEIGHT = 16


def switchState(state):
    """Switch between game states."""
    global currentScreen, gameScreen, initScreen, titleScreen, gameOverScreen, levelSelectionScreen, confirmScreen

    # Import screens here to avoid circular imports
    from init_screen import InitScreen
    from title_screen import TitleScreen
    from game_screen import GameScreen
    from game_over_screen import GameOverScreen
    from level_selection_screen import LevelSelectionScreen
    from confirm_screen import ConfirmScreen

    if state == 'init':
        if initScreen is None:
            initScreen = InitScreen()
        currentScreen = initScreen
    elif state == 'title':
        if titleScreen is None:
            titleScreen = TitleScreen()
        else:
            titleScreen.init()
        currentScreen = titleScreen
    elif state == 'levels':
        if levelSelectionScreen is None:
            levelSelectionScreen = LevelSelectionScreen()
        currentScreen = levelSelectionScreen
    elif state == 'game':
        if gameScreen is None:
            gameScreen = GameScreen()
        currentScreen = gameScreen
        reset_game_state()
    elif state == 'gameover':
        if gameOverScreen is None:
            gameOverScreen = GameOverScreen()
        currentScreen = gameOverScreen
    elif state == 'confirm':
        if confirmScreen is None:
            confirmScreen = ConfirmScreen()
        currentScreen = confirmScreen

    import ledwall

    if state != 'init':
        ledwall.cls()

    global tick
    tick = 0


def initialize_game_state():
    """Initialize the global game state."""
    global tick
    tick = 0

def reset_game_state():
    if gameScreen:
        gameScreen.players[0].score = 0
        gameScreen.players[1].score = 0
        gameScreen.players[0].ammo = config.INITIAL_AMMO
        gameScreen.players[1].ammo = config.INITIAL_AMMO
        gameScreen.players[0].xpos = config.PLAYER_1_STARTX * TILE_WIDTH
        gameScreen.players[0].ypos = config.PLAYER_1_STARTY * TILE_HEIGHT
        gameScreen.players[1].xpos = config.PLAYER_2_STARTX * TILE_WIDTH
        gameScreen.players[1].ypos = config.PLAYER_2_STARTY * TILE_HEIGHT

        gameScreen.players[0].sprite.speed = 6
        gameScreen.players[1].sprite.speed = 6

        gameScreen.objects.clear()  # Remove all bullets and weapon drops
        gameScreen.weapon_drop_timer = 0  # Reset weapon drop timer
        gameScreen.destroyed_cacti.clear()  # Reset cactus respawn timers

        # Reset bird circling behavior
        if hasattr(gameScreen, 'birds_circling'):
            gameScreen.birds_circling = False
            gameScreen.dead_player_x = 0
            gameScreen.dead_player_y = 0

        global message
        message = None

        controls.restore(0)
        controls.restore(1)

        # Reset level to original state
        from config import get_level_map_data
        original_mapdata = get_level_map_data()
        level.mapdata = original_mapdata[:]  # Create a copy

        if hasattr(gameScreen, 'winner'):
            delattr(gameScreen, 'winner')
