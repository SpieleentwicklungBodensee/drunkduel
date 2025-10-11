
"""
Game screen module for Drunk Duel.
Handles the main gameplay screen and player interactions.
"""

import pygame
import random

import config
import ledwall
import controls
import game_state
from base import Screen
from game_state import TILE_WIDTH, TILE_HEIGHT
from player import Player, load_player_sprites
from game_logic import checkCollisions, checkWeaponPickup, checkBeerPickup, checkHealthPickup, checkVictory, spawnWeaponDrop, spawnBeerPowerup, spawnHealthPowerup
from weapon_drop import WeaponDrop
from beer_powerup import BeerPowerup
from health_powerup import HealthPowerup

# Override print function
import ledwall
print = ledwall.print



class GameScreen(Screen):
    def __init__(self):
        super().__init__()

        self.players = []
        self.objects = []
        self.weapon_drop_timer = 0  # Timer for spawning weapon drops
        self.beer_spawn_timer = 0  # Timer for spawning beer powerups
        self.health_spawn_timer = 0  # Timer for spawning health powerups
        self.winner = None  # Track game winner

        # Cactus respawn system
        self.destroyed_cacti = []  # List of (destruction_time, respawn_time) tuples

        # Load player sprites and constants
        player1_sprite, player2_sprite = load_player_sprites()

        player1 = Player(2 * TILE_WIDTH, 2 * TILE_HEIGHT, player1_sprite)
        player2 = Player(13 * TILE_WIDTH, 13 * TILE_HEIGHT, player2_sprite)

        self.players.append(player1)
        self.players.append(player2)

        # Flag to spawn initial beer powerups on first update
        self.initial_spawn_done = False

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

        # Draw alcohol level display (nur wenn Alkohol aktiviert)
        if config.ALCOHOL_ENABLED:
            alcohol1_percent = int(self.players[0].alcohol_level * 100)
            alcohol2_percent = int(self.players[1].alcohol_level * 100)

            # Color coding: green = sober, yellow = tipsy, red = drunk
            def get_alcohol_color(level):
                if level <= 20:
                    return (0, 255, 0)  # Green
                elif level <= 50:
                    return (255, 255, 0)  # Yellow
                else:
                    return (255, 0, 0)  # Red

            alcohol1_color = get_alcohol_color(alcohol1_percent)
            alcohol2_color = get_alcohol_color(alcohol2_percent)

            ledwall.drawText(f'ALC: {alcohol1_percent}%', x=2, y=game_state.level.getHeight() * 2 + 2, color=alcohol1_color)
            ledwall.drawText(f'ALC: {alcohol2_percent}%', x=20, y=game_state.level.getHeight() * 2 + 2, color=alcohol2_color)

        # Draw health display
        def get_health_color(health):
            if health >= 75:
                return (0, 255, 0)  # Green
            elif health >= 50:
                return (255, 255, 0)  # Yellow
            elif health >= 25:
                return (255, 165, 0)  # Orange
            else:
                return (255, 0, 0)  # Red

        health1_color = get_health_color(self.players[0].health)
        health2_color = get_health_color(self.players[1].health)

        # Health-Position anpassen je nachdem ob Alkohol-HUD vorhanden ist
        if config.ALCOHOL_ENABLED:
            health_y_pos = game_state.level.getHeight() * 2 + (3 if config.ALCOHOL_ENABLED else 2)
            ledwall.drawText(f'HP: {self.players[0].health}', x=2, y=health_y_pos, color=health1_color)
            ledwall.drawText(f'HP: {self.players[1].health}', x=20, y=health_y_pos, color=health2_color)

            ledwall.drawText(f'HP: {self.players[0].health}', x=2, y=game_state.level.getHeight() * 2 + 3, color=health1_color)
            ledwall.drawText(f'HP: {self.players[1].health}', x=20, y=game_state.level.getHeight() * 2 + 3, color=health2_color)

            # Draw vomiting status
            if self.players[0].is_vomiting:
                ledwall.drawText('KOTZT', x=2, y=game_state.level.getHeight() * 2 + 4, color=(0, 255, 0))
            if self.players[1].is_vomiting:
                ledwall.drawText('KOTZT', x=20, y=game_state.level.getHeight() * 2 + 4, color=(0, 255, 0))

        # Draw level info and hotkeys
        self._draw_level_info()

    def event(self, e):
        if game_state.message:  # do not handle input while message is shown
            return

        if e.type == pygame.KEYDOWN:
            # Level navigation hotkeys
            if e.key == pygame.K_F3:  # Previous level
                self._switch_to_previous_level()
                return
            elif e.key == pygame.K_F4:  # Next level
                self._switch_to_next_level()
                return
            elif e.key == pygame.K_F5:  # Open level selection
                game_state.switchState('levels')
                return

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
                    # Pass the other player's position to determine shooting direction
                    other_player_index = 1 - i  # Get the other player (0->1, 1->0)
                    other_player_x = self.players[other_player_index].xpos
                    self.players[i].shoot(i, other_player_x)

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

        elif e.type in (pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            action = controls.handleJoyEvent(e)
            controls.performAction(action, self.players[e.instance_id], e.instance_id)

    def update(self):

        # Spawn initial beer powerups on first update
        if not self.initial_spawn_done:
            if config.ALCOHOL_ENABLED:
                self._spawn_initial_beer_powerups()
            self.initial_spawn_done = True

        for i, player in enumerate(self.players):
            # Update facing direction to look towards other player
            other_player_index = 1 - i
            other_player_x = self.players[other_player_index].xpos
            player.update_facing_direction(other_player_x)

            player.update()

        if game_state.message:  # do not handle rest of updates while message is shown
            game_state.message.update()
            return

        for obj in self.objects:
            obj.update()

        # Check for collisions
        checkCollisions()

        # Check for weapon pickups
        checkWeaponPickup()

        # Check for beer pickups
        checkBeerPickup()

        # Check for health pickups
        checkHealthPickup()

        # Check if a player has won
        checkVictory()

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

        # Spawn beer powerups periodically (nur wenn Alkohol aktiviert)
        if config.ALCOHOL_ENABLED:
            self.beer_spawn_timer += 1
            if self.beer_spawn_timer >= 120:  # Spawn every 2 seconds (120 frames at 60 FPS) für Test
                # Only spawn if there aren't too many beer powerups already
                beer_powerups = [obj for obj in self.objects if isinstance(obj, BeerPowerup)]
                if len(beer_powerups) < 2:  # Max 2 beer powerups on map
                    if random.random() < 0.8:  # 80% chance to spawn (erhöht für Test)
                        # Use the beer sprite from game state
                        if hasattr(game_state, 'beer_sprite'):
                            spawnBeerPowerup(game_state.beer_sprite)
                self.beer_spawn_timer = 0

        # Spawn health powerups periodically (less frequent)
        if config.ALCOHOL_ENABLED:
            self.health_spawn_timer += 1
            if self.health_spawn_timer >= 480:  # Spawn every 8 seconds (480 frames at 60 FPS)
                # Only spawn if there aren't too many health powerups already
                health_powerups = [obj for obj in self.objects if isinstance(obj, HealthPowerup)]
                if len(health_powerups) < 1:  # Max 1 health powerup on map
                    if random.random() < 0.3:  # 30% chance to spawn
                        # Use munition sprite as placeholder for health powerup
                        spawnHealthPowerup(game_state.medkit_sprite)
                self.health_spawn_timer = 0

        # Handle cactus respawning
        self._handle_cactus_respawn()

        # Remove expired powerups
        for obj in self.objects[:]:
            if isinstance(obj, (BeerPowerup, HealthPowerup)):
                if obj.update():  # Returns True if should be removed
                    self.removeObject(obj)

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

    def _switch_to_next_level(self):
        """Switch to the next level."""
        from level_loader import get_level_loader
        level_loader = get_level_loader()
        next_level = level_loader.next_level()
        self._reload_level_with_data(next_level)

    def _switch_to_previous_level(self):
        """Switch to the previous level."""
        from level_loader import get_level_loader
        level_loader = get_level_loader()
        prev_level = level_loader.previous_level()
        self._reload_level_with_data(prev_level)

    def _reload_level_with_data(self, level_data):
        """Reload the game with new level data."""
        try:
            from level import Level

            # Create new level with the new data
            game_state.level = Level(level_data.mapdata, game_state.level.tiles)

            # Reset player positions
            from config import PLAYER_1_STARTX, PLAYER_1_STARTY, PLAYER_2_STARTX, PLAYER_2_STARTY
            self.players[0].xpos = PLAYER_1_STARTX * TILE_WIDTH
            self.players[0].ypos = PLAYER_1_STARTY * TILE_HEIGHT
            self.players[1].xpos = PLAYER_2_STARTX * TILE_WIDTH
            self.players[1].ypos = PLAYER_2_STARTY * TILE_HEIGHT

            # Reset other game state
            self.objects.clear()

            # Reset timers
            self.weapon_drop_timer = 0
            self.beer_spawn_timer = 0
            self.health_spawn_timer = 0
            self.initial_spawn_done = False

            # Show level change message
            import game_state
            from message import Message
            game_state.message = Message(f"Level: {level_data.name}", 60)

            print(f"Switched to level: {level_data.name}")

        except Exception as e:
            print(f"Error switching level: {e}")

    def _draw_level_info(self):
        """Draw level information and hotkeys."""
        from level_loader import get_level_loader
        level_loader = get_level_loader()
        current_level = level_loader.get_current_level()
        level_count = level_loader.get_level_count()
        current_index = level_loader.current_level_index

        # Draw level name in top right corner
        level_text = f"{current_level.name} ({current_index + 1}/{level_count})"
        text_width = len(level_text) * 8  # Assume 8-pixel wide font
        screen_width = game_state.output.get_width()
        ledwall.drawText(level_text, x=screen_width - text_width - 5, y=2, color=(200, 200, 200))

    def _spawn_initial_beer_powerups(self):
        """Spawnt 1-2 Bier-Powerups beim Spielstart."""
        if hasattr(game_state, 'beer_sprite'):
            # Spawn 1-2 beer powerups at game start
            for _ in range(random.randint(1, 2)):
                spawnBeerPowerup(game_state.beer_sprite)

        # Also spawn 1 health powerup at start
        if hasattr(game_state, 'munition_sprite'):
            spawnHealthPowerup(game_state.munition_sprite)