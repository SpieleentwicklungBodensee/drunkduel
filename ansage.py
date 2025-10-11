#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 21:29:45 2025

@author: knoedel
"""

import pygame
import time
import sys

pygame.mixer.init()

# Predefined playlist (name -> file path)


SFX_rechts_d = pygame.mixer.Sound("sfx/rechts_d.wav")
SFX_links_d = pygame.mixer.Sound("sfx/links_d.wav")
SFX_oben_d = pygame.mixer.Sound("sfx/oben_d.wav")
SFX_unten_d = pygame.mixer.Sound("sfx/unten_d.wav")
SFX_ist_d = pygame.mixer.Sound("sfx/ist_d.wav")

playlist = {
    "rechts": SFX_rechts_d,
    "links": SFX_links_d,
    "oben": SFX_oben_d,
    "unten": SFX_unten_d,
    "ist": SFX_ist_d
}
def play(name):
    play_tracks([playlist[name]])


def play_tracks(tracks):
    """
    Play a list of audio files in order.
    :param tracks: list of file paths
    """
    #pygame.mixer.init()

    for track in tracks:
        print(f"▶️ Playing: {track}")
        #track.play()
        channel = track.play()
        while channel.get_busy():
            time.sleep(0.05)

    #pygame.mixer.quit()
    print("✅ Done.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sound_player.py track_name1 track_name2 ...")
        print("Available tracks:", ", ".join(playlist.keys()))
        sys.exit(1)

    track_names = sys.argv[1:]
    tracks_to_play = []

    # Convert names to file paths
    for name in track_names:
        if name in playlist:
            tracks_to_play.append(playlist[name])
        else:
            print(f"⚠️ Warning: '{name}' is not in the playlist. Skipping.")

    if not tracks_to_play:
        print("No valid tracks to play. Exiting.")
        sys.exit(1)

    play_tracks(tracks_to_play)


