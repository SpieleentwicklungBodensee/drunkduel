"""
Sound management module for Drunk Duel.
Centralizes all sound loading and playback functionality.
"""

import pygame


# Sound effects
SFX_GUNSHOT = None
SFX_FOOTSTEP = None
SFX_RICOCHET = None
SFX_PLAYER_HIT = None
SFX_EXPLOSION = None
SFX_BEER_PICKUP = None  # Neuer Sound für Bier-Pickup
SFX_VOMIT = None  # Neuer Sound für Kotzen

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


def playFootstepSound():
    """Play footstep sound with timing control."""
    global lastPlayedFootstep
    from game_state import tick
    
    if tick != lastPlayedFootstep:
        SFX_FOOTSTEP.play()
        lastPlayedFootstep = tick