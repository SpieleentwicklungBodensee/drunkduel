"""
Main entry point for Drunk Duel game.
Handles initialization and main game loop.
"""

import pygame

import ledwall
import game_state
import controls
import config
from config import (
    parse_arguments, load_settings, validate_render_mode,
    get_default_brightness, initialize_joysticks, load_graphics,
    get_level_map_data, print_startup_info
)
from sound_manager import load_sounds
from level import Level
from level_loader import initialize_levels
from game_state import initialize_game_state, switchState

# Initialize Mixer for sound first
pygame.mixer.init()

# Override print function
print = ledwall.print


def initialize_game():
    """Initialize all game components."""
    global BRIGHTNESS

    # Parse command line arguments
    args = parse_arguments()

    # Load settings
    settings = load_settings()
    render_mode = settings['RENDER_MODE']
    default_brightness = settings['DEFAULT_BRIGHTNESS']

    # Override with command line if provided
    if args.rendermode:
        render_mode = args.rendermode
        validate_render_mode(render_mode)

    # Set brightness
    if default_brightness is None:
        default_brightness = get_default_brightness(render_mode)

    BRIGHTNESS = default_brightness
    game_state.BRIGHTNESS = BRIGHTNESS

    # Initialize display
    game_state.output = ledwall.initScreen(render_mode)
    ledwall.setBrightnessValue(BRIGHTNESS)

    # Initialize clock
    game_state.clock = pygame.time.Clock()

    # Initialize joysticks
    joysticks, num_joysticks = initialize_joysticks()
    controls.JOYSTICKS += joysticks

    # Load graphics and sounds
    tiles, bullet_sprite, munition_sprite, beer_sprite, medkit_sprite = load_graphics()
    load_sounds()

    # Initialize level system
    initialize_levels()

    # Store sprites in game state for access by other modules
    game_state.bullet_sprite = bullet_sprite
    game_state.munition_sprite = munition_sprite
    game_state.beer_sprite = beer_sprite
    game_state.medkit_sprite = medkit_sprite

    # Create level
    mapdata = get_level_map_data()
    game_state.level = Level(mapdata, tiles)

    # Set Duck Hunt mode based on initial level
    from level_loader import get_level_loader
    level_loader = get_level_loader()
    current_level = level_loader.get_current_level()
    config.DUCK_HUNT_MODE = current_level.duck_hunt_mode
    config.ALLOW_UP_DOWN_SHOOT = current_level.allow_up_down_shoot

    # Print startup info
    print_startup_info(render_mode, num_joysticks)

    # Initialize game state
    initialize_game_state()

    return render_mode


def handle_global_events(event, render_mode):
    """Handle global game events like brightness and fullscreen."""
    global BRIGHTNESS

    if event.type == pygame.QUIT:
        return False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            # Only allow ESC to exit the game from certain screens (title, init)
            # During gameplay, let the game screen handle ESC to return to menu
            current_state = getattr(game_state, 'currentScreen', None)
            if current_state and hasattr(current_state, '__class__'):
                screen_name = current_state.__class__.__name__
                # Allow ESC to quit from title screen, init screen, or level selection
                if screen_name in ['TitleScreen', 'InitScreen', 'LevelSelectionScreen']:
                    return False
                # For other screens (like GameScreen), let them handle ESC themselves
            else:
                # If we can't determine the screen, default to quitting
                return False
        elif event.key == pygame.K_F1:
            BRIGHTNESS -= 1
            game_state.BRIGHTNESS = BRIGHTNESS
            ledwall.setBrightnessValue(BRIGHTNESS)
        elif event.key == pygame.K_F2:
            BRIGHTNESS += 1
            if BRIGHTNESS > 0:
                BRIGHTNESS = 0
            game_state.BRIGHTNESS = BRIGHTNESS
            ledwall.setBrightnessValue(BRIGHTNESS)
        elif event.key == pygame.K_F11 and render_mode != 'led':
            pygame.display.toggle_fullscreen()

    return True


def main():
    """Main game loop."""
    render_mode = initialize_game()

    # Initialize screens
    switchState('init')

    running = True

    while running:
        # Draw
        game_state.output.fill((0, 0, 0))
        game_state.currentScreen.draw()
        ledwall.compose(do_cls=False)

        # Handle events
        events = pygame.event.get()

        for event in events:
            if not handle_global_events(event, render_mode):
                running = False
                break
            else:
                game_state.currentScreen.event(event)

        if not running:
            break

        # Update
        game_state.currentScreen.update()

        # Tick
        game_state.clock.tick(60)
        game_state.tick += 1


if __name__ == "__main__":
    main()
