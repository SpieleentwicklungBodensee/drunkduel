
"""
Game screen module for Drunk Duel.
Handles the main gameplay screen and player interactions.
"""

import pygame
import random

import ledwall
import controls
import config
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

        # Cactus respawn system
        self.destroyed_cacti = []  # List of (destruction_time, respawn_time) tuples

        # Load player sprites and constants
        player1_sprite, player2_sprite = load_player_sprites()

        player1 = Player(config.PLAYER_1_STARTX * TILE_WIDTH, config.PLAYER_1_STARTY * TILE_HEIGHT, player1_sprite)
        player2 = Player(config.PLAYER_2_STARTX * TILE_WIDTH, config.PLAYER_2_STARTY * TILE_HEIGHT, player2_sprite)

        self.players.append(player1)
        self.players.append(player2)

    def draw(self):
        game_state.level.draw(game_state.output)

        for player in self.players:
            player.draw(game_state.output)

        for obj in self.objects:
            obj.draw(game_state.output)

        # draw message
        if game_state.message:
            game_state.message.draw(game_state.output)

            if game_state.message.isDue():
                game_state.message = None

        # Draw highscore display
        ledwall.drawText(f'HITS: {self.players[0].score}', x=2, y=game_state.level.getHeight() * 2, color=(255, 255, 0))
        ledwall.drawText(f'HITS: {self.players[1].score}', x=20, y=game_state.level.getHeight() * 2, color=(255, 255, 0))

        # Draw ammo display with color coding - P1 left, P2 right
        ammo1_color = (255, 255, 255) if self.players[0].ammo > 0 else (255, 0, 0)
        ammo2_color = (255, 255, 255) if self.players[1].ammo > 0 else (255, 0, 0)

        ledwall.drawText(f'AMMO: {self.players[0].ammo}', x=2, y=game_state.level.getHeight() * 2 + 1, color=ammo1_color)
        ledwall.drawText(f'AMMO: {self.players[1].ammo}', x=20, y=game_state.level.getHeight() * 2 + 1, color=ammo2_color)

    def event(self, e):
        if game_state.message:      # pause if message is displayed
            return

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
        if game_state.message:      # pause if message is displayed
            return

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

        # Handle cactus respawning
        self._handle_cactus_respawn()

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        self.objects.remove(obj)

    def schedule_cactus_respawn(self):
        """Schedule a new cactus to respawn after 5-10 seconds."""
        current_time = game_state.tick
        # Random respawn time between 5-10 seconds (300-600 frames at 60 FPS)
        respawn_delay = random.randint(300, 600)
        respawn_time = current_time + respawn_delay
        self.destroyed_cacti.append(respawn_time)

    def _handle_cactus_respawn(self):
        """Check if any cacti are ready to respawn and spawn them."""
        current_time = game_state.tick

        # Check all scheduled respawns
        for respawn_time in self.destroyed_cacti[:]:  # Use slice to avoid modification during iteration
            if current_time >= respawn_time:
                # Time to respawn a cactus
                self._spawn_new_cactus()
                self.destroyed_cacti.remove(respawn_time)

    def _spawn_new_cactus(self):
        """Spawn a new cactus at a random empty location."""
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            x = random.randint(0, game_state.level.getWidth() - 1)
            y = random.randint(0, game_state.level.getHeight() - 1)

            tile = game_state.level.getTile(x, y)

            # Check if the location is empty and suitable for a cactus
            if tile == ' ':
                # Also check if there are no players or objects too close
                tile_center_x = x * TILE_WIDTH + TILE_WIDTH // 2
                tile_center_y = y * TILE_HEIGHT + TILE_HEIGHT // 2

                # Ensure cactus doesn't spawn too close to players
                too_close = False
                for player in self.players:
                    player_center_x = player.xpos + TILE_WIDTH // 2
                    player_center_y = player.ypos + TILE_HEIGHT // 2
                    distance_sq = (tile_center_x - player_center_x) ** 2 + (tile_center_y - player_center_y) ** 2
                    if distance_sq < (TILE_WIDTH * 3) ** 2:  # At least 3 tiles away
                        too_close = True
                        break

                if not too_close:
                    # Spawn the cactus
                    game_state.level.setTile(x, y, 'Y')
                    break

            attempts += 1