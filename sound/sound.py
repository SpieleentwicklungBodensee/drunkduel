#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 21:29:45 2025

@author: knoedel
"""

import pygame
import time

pygame.mixer.init()

playlist = [
    "rechts.mp3",
    "links.mp3",
    "oben.mp3",
    "unten.mp3",
    "ist.mp3"
]

for file in playlist:
    print(f"▶️ Spiele ab: {file}")
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    
    time.sleep(0.1)  # small delay ensures first sound isn't cut off

    # Warten, bis der Track fertig ist
    while pygame.mixer.music.get_busy():
        time.sleep(0.06)
   
        
file=playlist[0]   
print(f"▶️ Spiele ab: {file}")
pygame.mixer.music.load(file)
pygame.mixer.music.play()
 # Warten, bis der Track fertig ist
while pygame.mixer.music.get_busy():
    time.sleep(0.06)
    
          
file=playlist[4]   
print(f"▶️ Spiele ab: {file}")
pygame.mixer.music.load(file)
pygame.mixer.music.play()
 # Warten, bis der Track fertig ist
while pygame.mixer.music.get_busy():
    time.sleep(0.06)
    
        
file=playlist[3]   
print(f"▶️ Spiele ab: {file}")
pygame.mixer.music.load(file)
pygame.mixer.music.play()
 # Warten, bis der Track fertig ist
while pygame.mixer.music.get_busy():
    time.sleep(0.06)    
    


pygame.mixer.quit()
print("✅ Fertig.")