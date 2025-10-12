"""
Game state management module.
Contains global game state variables and state switching logic.
"""

import controls
import config
import sound_manager
from level_loader import LevelLoader
import level_loader

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
        # Reset single-player mode and Duck Hunt mode when returning to title
        config.SINGLEPLAYER_MODE = False
        config.DUCK_HUNT_MODE = False
        # Stop any playing music
        from sound_manager import stop_music
        stop_music()
        
        # Reset the game screen to force recreation with correct settings
        global gameScreen
        gameScreen = None
        
        # Restore original level loader if we were in duck hunt mode
        if hasattr(level_loader.level_loader, 'levels_directory') and 'duckhunt' in level_loader.level_loader.levels_directory:
            # We were using the duck hunt loader, restore the main one
            main_loader = LevelLoader("levels")
            main_loader.load_all_levels()
            if main_loader.get_level_count() > 0:
                main_loader.set_current_level(0)  # Set to first level
                level_loader.level_loader = main_loader
                
                # Update the current level in game state
                global level
                if level:
                    from level import Level
                    from config import load_graphics
                    try:
                        tiles = level.tiles if hasattr(level, 'tiles') else load_graphics()[0]
                        current_level_data = main_loader.get_current_level()
                        level = Level(current_level_data.mapdata, tiles)
                        # Explicitly disable duck hunt mode when restoring main levels
                        config.DUCK_HUNT_MODE = False
                        config.ALLOW_UP_DOWN_SHOOT = current_level_data.allow_up_down_shoot
                    except Exception as e:
                        if config.DEBUG_MODE:
                            print(f"Error restoring main level: {e}")
        
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
        sound_manager.SFX_GAME_OVER_GUITAR.play()
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
        # Reset single-player mode variables
        if hasattr(gameScreen, 'bird_score'):
            gameScreen.bird_score = 0

        # Only reset second player if not in single-player mode
        if not getattr(config, 'SINGLEPLAYER_MODE', False):
            if len(gameScreen.players) > 1:
                gameScreen.players[1].score = 0
                gameScreen.players[1].ammo = config.INITIAL_AMMO
                gameScreen.players[1].xpos = config.PLAYER_2_STARTX * TILE_WIDTH
                gameScreen.players[1].ypos = config.PLAYER_2_STARTY * TILE_HEIGHT
                gameScreen.players[1].sprite.speed = 6

        # Always reset first player
        gameScreen.players[0].score = 0
        gameScreen.players[0].ammo = config.INITIAL_AMMO
        gameScreen.players[0].xpos = config.PLAYER_1_STARTX * TILE_WIDTH
        gameScreen.players[0].ypos = config.PLAYER_1_STARTY * TILE_HEIGHT
        gameScreen.players[0].sprite.speed = 6

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
