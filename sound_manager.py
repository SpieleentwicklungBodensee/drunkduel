"""
Sound management module for Drunk Duel.
Centralizes all sound loading and playback functionality.
"""

import pygame
import os

# Override print function
import ledwall
print = ledwall.print



# Sound effects
SFX_GUNSHOT = None
SFX_FOOTSTEP = None
SFX_RICOCHET = None
SFX_PLAYER_HIT = None
SFX_EXPLOSION = None
SFX_BEER_PICKUP = None  # Neuer Sound für Bier-Pickup
SFX_VOMIT = None  # Neuer Sound für Kotzen
SFX_RELOAD = None
SFX_NOAMMO = None

# Sound words
SOUND_WORDS = {}

# Laughing sounds for beer drinking
SFX_LAUGHING = []  # List of laughing sounds

# Footstep timing
lastPlayedFootstep = 0


def load_sounds():
    """Load all game sound effects."""
    global SFX_GUNSHOT, SFX_FOOTSTEP, SFX_RICOCHET, SFX_PLAYER_HIT, SFX_EXPLOSION, SFX_BEER_PICKUP, SFX_VOMIT, SFX_LAUGHING, SFX_BORING, SFX_RELOAD, SFX_NOAMMO

    print('loading sfx...')
    SFX_GUNSHOT = pygame.mixer.Sound("sfx/Gunshot.wav")
    SFX_FOOTSTEP = pygame.mixer.Sound("sfx/Footstep.wav")
    SFX_RICOCHET = pygame.mixer.Sound("sfx/Ricochet.wav")
    SFX_PLAYER_HIT = pygame.mixer.Sound("sfx/Wilhelm_Scream.wav")
    SFX_EXPLOSION = pygame.mixer.Sound("sfx/Explosion.wav")
    # Für Bier-Pickup verwenden wir erstmal den Footstep-Sound
    SFX_BEER_PICKUP = SFX_FOOTSTEP
    # Für Kotzen verwenden wir erstmal einen existierenden Sound
    SFX_VOMIT = pygame.mixer.Sound("sfx/Kotz.wav")
    SFX_BORING = pygame.mixer.Sound("sfx/Boring.wav")
    SFX_RELOAD = pygame.mixer.Sound("sfx/Reload.wav")
    SFX_NOAMMO = pygame.mixer.Sound("sfx/No_Ammo.wav")

    # Load multiple laughing sounds
    # Find all laughing sound files by parsing filenames
    for filename in os.listdir("sfx"):
        if filename.startswith("laughing") and filename.endswith(".wav"):
            sound = pygame.mixer.Sound(os.path.join("sfx", filename))
            SFX_LAUGHING.append(sound)

    SOUND_WORDS['links'] = (pygame.mixer.Sound('sfx/links_01_d.wav'),
                            pygame.mixer.Sound('sfx/links_02_d.wav'))

    SOUND_WORDS['rechts'] = (pygame.mixer.Sound('sfx/rechts_01_d.wav'),
                             pygame.mixer.Sound('sfx/rechts_02_d.wav'))

    SOUND_WORDS['oben'] = (pygame.mixer.Sound('sfx/oben_01_d.wav'),
                           pygame.mixer.Sound('sfx/oben_02_d.wav'))

    SOUND_WORDS['unten'] = (pygame.mixer.Sound('sfx/unten_01_d.wav'),
                             pygame.mixer.Sound('sfx/unten_02_d.wav'))

    SOUND_WORDS['feuer'] = (pygame.mixer.Sound('sfx/feuer_01_d.wav'),
                            pygame.mixer.Sound('sfx/feuer_02_d.wav'))

    SOUND_WORDS['ist'] = pygame.mixer.Sound('sfx/ist_d.wav')

    SOUND_WORDS['spieler 1:'] = pygame.mixer.Sound('sfx/spieler_eins_d.wav')
    SOUND_WORDS['spieler 2:'] = pygame.mixer.Sound('sfx/spieler_zwei_d.wav')

    SOUND_WORDS['spieler'] = pygame.mixer.Sound('sfx/spieler_d.wav')
    SOUND_WORDS['eins'] = pygame.mixer.Sound('sfx/eins_d.wav')
    SOUND_WORDS['zwei'] = pygame.mixer.Sound('sfx/zwei_d.wav')
    SOUND_WORDS['game_over'] = pygame.mixer.Sound('sfx/game_over_d.wav')
    SOUND_WORDS['wins'] = pygame.mixer.Sound('sfx/wins_d.wav')

def playFootstepSound():
    """Play footstep sound with timing control."""
    global lastPlayedFootstep
    from game_state import tick

    if tick != lastPlayedFootstep:
        SFX_FOOTSTEP.play()
        lastPlayedFootstep = tick