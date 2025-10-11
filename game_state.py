"""
Game state management module.
Contains global game state variables and state switching logic.
"""

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
        currentScreen = titleScreen
    elif state == 'levels':
        if levelSelectionScreen is None:
            levelSelectionScreen = LevelSelectionScreen()
        currentScreen = levelSelectionScreen
    elif state == 'game':
        if gameScreen is None:
            gameScreen = GameScreen()
        currentScreen = gameScreen
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