"""
Configuration and initialization module for Drunk Duel.
Handles command line arguments, settings, and initial setup.
"""

import argparse
import pygame
from sprite import Sprite, createAnimatedSprite

# Override print function
import ledwall
print = ledwall.print


PLAYER_1_STARTX = 2
PLAYER_1_STARTY = 2
PLAYER_2_STARTX = 13
PLAYER_2_STARTY = 13

INITIAL_AMMO = 4
REWARD_AMMO = 0

# Sprachausgabe-Einstellungen
ACCURATE_INTONATION = False # wenn True, klingen die saetze langweiliger

# Alkohol-Einstellungen
ALCOHOL_ENABLED = True  # Wird durch den Startbildschirm gesetzt


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog='Drunk Duel')
    parser.add_argument('--rendermode', default=None, help='possible modes: plain, led')
    return parser.parse_args()


def load_settings():
    """Load settings from settings.py file with defaults."""
    settings = {}

    # Try to load settings from settings.py
    try:
        for attr in dir(settings):
            if not attr.startswith('_'):
                settings[attr] = getattr(settings, attr)
    except ImportError:
        pass

    # Set defaults if not defined
    if 'RENDER_MODE' not in settings:
        settings['RENDER_MODE'] = 'plain'

    if 'DEFAULT_BRIGHTNESS' not in settings:
        settings['DEFAULT_BRIGHTNESS'] = None

    return settings


def validate_render_mode(render_mode):
    """Validate the render mode setting."""
    if render_mode not in ['plain', 'led']:
        print('unknown rendermode: %s' % render_mode)
        exit(1)


def get_default_brightness(render_mode):
    """Get default brightness based on render mode."""
    if render_mode == 'led':
        return -4
    else:
        return 0


def initialize_joysticks():
    """Initialize and detect joysticks."""
    pygame.joystick.init()
    numJoysticks = pygame.joystick.get_count()
    joysticks = []

    if numJoysticks == 0:
        print('no joysticks found')
    else:
        print('joysticks found:')
        for i in range(numJoysticks):
            joystick = pygame.joystick.Joystick(i)
            joysticks.append(joystick)
            print('-', joystick.get_name())

    return joysticks, numJoysticks


def load_graphics():
    """Load all game graphics and sprites."""
    print('loading gfx...')

    tiles = {
        'Y': Sprite('gfx/desert3.png'),
        '|': createAnimatedSprite('gfx/water1.png'),
        '#': Sprite('gfx/fence1.png'),
        'o': Sprite('gfx/stone1.png'),
        'F': None,  # Invisible wall
        ' ': None,
    }

    bullet_sprite = Sprite('gfx/bullet.png')
    munition_sprite = Sprite('gfx/munition.png')
    beer_sprite = Sprite('gfx/bier.png')
    medkit_sprite = Sprite('gfx/med1.png')

    # Animate water
    tiles['|'].speed = 12
    tiles['|'].start()

    return tiles, bullet_sprite, munition_sprite, beer_sprite, medkit_sprite


def get_level_map_data():
    """Get the current level map data from the level loader."""
    from level_loader import get_current_level_data
    return get_current_level_data()


def print_startup_info(render_mode, num_joysticks):
    """Print startup information and controls."""
    print('welcome to drunk duel')
    print('---------------------')
    print()
    print('rendermode: %s' % render_mode)
    print()
    print('\n')
    print('keyboard:')
    print('---------')
    print('f1   less brightness')
    print('f2   more brightness')
    print()

    if render_mode != 'led':
        print('f11  toggle fullscreen')

    print('\n\n')

    if num_joysticks == 0:
        print('press space to continue')
    else:
        print('press space or button')