"""
Sound management module for Drunk Duel.
Centralizes all sound loading and playback functionality.
"""

import pygame
import os

# Sound effects
SFX_GUNSHOT = None
SFX_FOOTSTEP = None
SFX_RICOCHET = None
SFX_PLAYER_HIT = None
SFX_EXPLOSION = None
SFX_BEER_PICKUP = None  # Neuer Sound für Bier-Pickup
SFX_VOMIT = None  # Neuer Sound für Kotzen

# Laughing sounds for beer drinking
SFX_LAUGHING = []  # List of laughing sounds

# Footstep timing
lastPlayedFootstep = 0


def load_sounds():
    """Load all game sound effects."""
    global SFX_GUNSHOT, SFX_FOOTSTEP, SFX_RICOCHET, SFX_PLAYER_HIT, SFX_EXPLOSION, SFX_BEER_PICKUP, SFX_VOMIT
    
    print('loading sfx...')
    SFX_GUNSHOT = pygame.mixer.Sound("sfx/Gunshot.wav")
    SFX_FOOTSTEP = pygame.mixer.Sound("sfx/Footstep.wav")
    SFX_RICOCHET = pygame.mixer.Sound("sfx/Ricochet.wav")
    SFX_PLAYER_HIT = pygame.mixer.Sound("sfx/Wilhelm_Scream.wav")
    SFX_EXPLOSION = pygame.mixer.Sound("sfx/Explosion.wav")
    # Für Bier-Pickup verwenden wir erstmal den Footstep-Sound
    SFX_BEER_PICKUP = SFX_FOOTSTEP
    # Für Kotzen verwenden wir erstmal einen existierenden Sound
    SFX_VOMIT = SFX_PLAYER_HIT  # Könnte später durch echten Kotz-Sound ersetzt werden

    # Load multiple laughing sounds
    # Find all laughing sound files by parsing filenames
    for filename in os.listdir("sfx"):
        if filename.startswith("laughing") and filename.endswith(".wav"):
            sound = pygame.mixer.Sound(os.path.join("sfx", filename))
            SFX_LAUGHING.append(sound)


def playFootstepSound():
    """Play footstep sound with timing control."""
    global lastPlayedFootstep
    from game_state import tick
    
    if tick != lastPlayedFootstep:
        SFX_FOOTSTEP.play()
        lastPlayedFootstep = tick