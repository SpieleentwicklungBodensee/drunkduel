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

# Bird sound effects
SFX_BIRD_HIT = None
SFX_BIRD_EXPLODING = None
SFX_BIRD_LAUNCH = None
SFX_GAME_OVER_GUITAR = None # Das Spiel ist aus!


# Sound words
SOUND_WORDS = {}

# Music
CURRENT_MUSIC = None

# Laughing sounds for beer drinking
SFX_LAUGHING = []  # List of laughing sounds

# Footstep timing
lastPlayedFootstep = 0


def load_sounds():
    """Load all game sound effects."""
    global SFX_GUNSHOT, SFX_FOOTSTEP, SFX_RICOCHET, SFX_PLAYER_HIT, SFX_EXPLOSION, SFX_BEER_PICKUP, SFX_VOMIT, SFX_LAUGHING, SFX_BORING, SFX_RELOAD, SFX_NOAMMO
    global SFX_BIRD_HIT, SFX_BIRD_EXPLODING, SFX_BIRD_LAUNCH
    global SFX_GAME_OVER_GUITAR

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

    SFX_GAME_OVER_GUITAR = pygame.mixer.Sound("sfx/Game_Over_Guitar.wav")

    # Load bird sound effects
    SFX_BIRD_HIT = pygame.mixer.Sound("sfx/Bird_getting_hit.wav")
    SFX_BIRD_EXPLODING = pygame.mixer.Sound("sfx/Bird_exploding.wav")
    SFX_BIRD_LAUNCH = pygame.mixer.Sound("sfx/Bird_launch.wav")

    # Ammo sounds
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


def play_music(music_file):
    """Play background music from the music directory."""
    global CURRENT_MUSIC
    try:
        if CURRENT_MUSIC != music_file:
            pygame.mixer.music.stop()
            music_path = os.path.join("music", music_file)
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                CURRENT_MUSIC = music_file
                print(f"Playing music: {music_file}")
            else:
                print(f"Music file not found: {music_path}")
    except Exception as e:
        print(f"Error playing music {music_file}: {e}")


def stop_music():
    """Stop background music."""
    global CURRENT_MUSIC
    try:
        pygame.mixer.music.stop()
        CURRENT_MUSIC = None
        print("Music stopped")
    except Exception as e:
        print(f"Error stopping music: {e}")


def set_music_volume(volume):
    """Set music volume (0.0 to 1.0)."""
    try:
        pygame.mixer.music.set_volume(volume)
    except Exception as e:
        print(f"Error setting music volume: {e}")
