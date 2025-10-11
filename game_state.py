"""
Game state management module.
Contains global game state variables and state switching logic.
"""

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
level = None
output = None
message = None

# Constants
TILE_WIDTH = 16
TILE_HEIGHT = 16

def switchState(state):
    """Switch between game states."""
    global currentScreen, gameScreen, initScreen, titleScreen, gameOverScreen

    # Import screens here to avoid circular imports
    from init_screen import InitScreen
    from title_screen import TitleScreen
    from game_screen import GameScreen
    from game_over_screen import GameOverScreen

    if state == 'init':
        if initScreen is None:
            initScreen = InitScreen()
        currentScreen = initScreen
    elif state == 'title':
        if titleScreen is None:
            titleScreen = TitleScreen()
        currentScreen = titleScreen
    elif state == 'game':
        if gameScreen is None:
            gameScreen = GameScreen()
        currentScreen = gameScreen
    elif state == 'gameover':
        if gameOverScreen is None:
            gameOverScreen = GameOverScreen()
        currentScreen = gameOverScreen

    import ledwall
    ledwall.cls()


def initialize_game_state():
    """Initialize the global game state."""
    global tick
    tick = 0