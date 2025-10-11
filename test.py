#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 22:37:32 2025

@author: knoedel
"""
from ansage import play, play_tracks, playlist
import pygame
import time
import random


#pygame.mixer.init()


# Select tracks by their names from the predefined playlist
#selected_names = ["links", "ist", "oben"]

# Convert names to file paths
#tracks_to_play = [playlist[name] for name in selected_names]

# Play the tracks
#play_tracks(tracks_to_play)

#sequential call 
play("rechts")
time.sleep(0.2)
play("ist")
time.sleep(0.2)
play("links")



#create random output

# Possible choices for first and third sounds
options = ["rechts", "links", "oben", "unten"]

# Randomly select first and third sounds without repetition
first, third = random.sample(options, 2)

# Build the sequence: first, ist, third
sequence = [first, "ist", third]

print("🎲 Random sequence:", sequence)

# Play the sequence
play(sequence[0])
time.sleep(0.2)
play(sequence[1])
time.sleep(0.2)
play(sequence[2])

pygame.mixer.quit()