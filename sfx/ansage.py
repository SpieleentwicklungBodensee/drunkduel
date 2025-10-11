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
playlist = {
    "rechts": "rechts.wav",
    "links": "links.wav",
    "oben": "oben.wav",
    "unten": "unten.wav",
    "ist": "ist.wav"
}


def play_tracks(tracks):
    """
    Play a list of audio files in order.
    :param tracks: list of file paths
    """
    pygame.mixer.init()

    for file in tracks:
        print(f"▶️ Playing: {file}")
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

        #time.sleep(0.1)  # ensure the first sound isn't cut off

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    pygame.mixer.quit()
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


