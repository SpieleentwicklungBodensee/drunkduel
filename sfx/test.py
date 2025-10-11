#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 22:37:32 2025

@author: knoedel
"""
from ansage import play_tracks, playlist

#create random output



# Select tracks by their names from the predefined playlist
selected_names = ["links", "ist", "oben"]

# Convert names to file paths
tracks_to_play = [playlist[name] for name in selected_names]

# Play the tracks
play_tracks(tracks_to_play)
