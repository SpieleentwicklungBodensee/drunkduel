
"""
Game screen module for Drunk Duel.
Handles the main gameplay screen and player interactions.
"""

import pygame
import random

import ledwall
import controls
import game_state
from base import Screen
from game_state import TILE_WIDTH, TILE_HEIGHT
from player import Player, load_player_sprites
from game_logic import checkCollisions, checkWeaponPickup, spawnWeaponDrop
from weapon_drop import WeaponDrop

class GameScreen(Screen):
    def __init__(self):
        super().__init__()

        self.players = []
        self.objects = []
        self.weapon_drop_timer = 0  # Timer for spawning weapon drops
        self.winner = None  # Track game winner

        # Load player sprites and constants
        player1_sprite, player2_sprite = load_player_sprites()
        
        player1 = Player(2 * TILE_WIDTH, 2 * TILE_HEIGHT, player1_sprite)
        player2 = Player(13 * TILE_WIDTH, 13 * TILE_HEIGHT, player2_sprite)

        self.players.append(player1)
        self.players.append(player2)

    def draw(self):
        game_state.level.draw(game_state.output)

        for player in self.players:
            player.draw(game_state.output)

        for obj in self.objects:
            obj.draw(game_state.output)

        # Draw highscore display
        ledwall.drawText(f'P1: {self.players[0].score}', x=2, y=game_state.level.getHeight() * 2, color=(255, 255, 0))
        ledwall.drawText(f'P2: {self.players[1].score}', x=20, y=game_state.level.getHeight() * 2, color=(255, 255, 0))

        # Draw ammo display with color coding - P1 left, P2 right
        ammo1_color = (255, 255, 255) if self.players[0].ammo > 0 else (255, 0, 0)
        ammo2_color = (255, 255, 255) if self.players[1].ammo > 0 else (255, 0, 0)

        ledwall.drawText(f'AMMO: {self.players[0].ammo}', x=2, y=game_state.level.getHeight() * 2 + 1, color=ammo1_color)
        ledwall.drawText(f'AMMO: {self.players[1].ammo}', x=20, y=game_state.level.getHeight() * 2 + 1, color=ammo2_color)

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            for i, keys in enumerate([controls.PLAYER_1_KEYS, controls.PLAYER_2_KEYS]):
                if e.key == keys[controls.DIR_LEFT]:
                    self.players[i].moveLeft()
                elif e.key == keys[controls.DIR_RIGHT]:
                    self.players[i].moveRight()
                elif e.key == keys[controls.DIR_UP]:
                    self.players[i].moveUp()
                elif e.key == keys[controls.DIR_DOWN]:
                    self.players[i].moveDown()

                elif e.key == keys[controls.FIRE]:
                    self.players[i].shoot(i)

        elif e.type == pygame.KEYUP:
            for i, keys in enumerate([controls.PLAYER_1_KEYS, controls.PLAYER_2_KEYS]):
                if e.key == keys[controls.DIR_LEFT]:
                    self.players[i].stopLeft()
                elif e.key == keys[controls.DIR_RIGHT]:
                    self.players[i].stopRight()
                elif e.key == keys[controls.DIR_UP]:
                    self.players[i].stopUp()
                elif e.key == keys[controls.DIR_DOWN]:
                    self.players[i].stopDown()

                elif e.key == keys[controls.FIRE]:
                    self.players[i].stopShooting()

    def update(self):
        for player in self.players:
            player.update()

        for obj in self.objects:
            obj.update()

        # Check for collisions
        checkCollisions()

        # Check for weapon pickups
        checkWeaponPickup()

        # Spawn weapon drops periodically
        self.weapon_drop_timer += 1
        if self.weapon_drop_timer >= 300:  # Spawn every 5 seconds (300 frames at 60 FPS)
            # Only spawn if there aren't too many weapon drops already
            weapon_drops = [obj for obj in self.objects if isinstance(obj, WeaponDrop)]
            if len(weapon_drops) < 3:  # Max 3 weapon drops on map
                if random.random() < 0.7:  # 70% chance to spawn
                    # Get munition sprite from game state
                    if hasattr(game_state, 'munition_sprite'):
                        spawnWeaponDrop(game_state.munition_sprite)
                    else:
                        # Fallback: create sprite directly
                        from sprite import Sprite
                        munition_sprite = Sprite('gfx/munition.png')
                        spawnWeaponDrop(munition_sprite)
            self.weapon_drop_timer = 0

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        self.objects.remove(obj)