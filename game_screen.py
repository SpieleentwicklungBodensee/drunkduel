
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
from bird import Bird, FenceBird
from sprite import createAnimatedSprite
from sound_manager import SFX_BIRD_LAUNCH

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
        self.bird_spawn_timer = 0  # Timer for spawning birds
        self.winner = None  # Track game winner

        # Cactus respawn system
        self.destroyed_cacti = []  # List of (destruction_time, respawn_time) tuples
        
        # Bird circling behavior
        self.birds_circling = False  # Track if birds are in circling mode
        self.dead_player_x = 0  # Position of dead player for circling
        self.dead_player_y = 0

        # Single-player mode variables
        self.bird_score = 0  # Score for hitting birds in single-player mode
        self.target_bird_score = 20  # Target score to win in single-player mode

        # Load player sprites and constants
        player1_sprite, player2_sprite = load_player_sprites()

        # Position player at bottom of map in Duck Hunt mode
        if getattr(config, 'DUCK_HUNT_MODE', False):
            # Duck Hunt: place player at bottom center of map
            duck_hunt_x = (game_state.level.getWidth() // 2) * TILE_WIDTH
            duck_hunt_y = (game_state.level.getHeight() - 2) * TILE_HEIGHT  # Bottom of map with small margin
            player1 = Player(duck_hunt_x, duck_hunt_y, player1_sprite)
        else:
            player1 = Player(2 * TILE_WIDTH, 2 * TILE_HEIGHT, player1_sprite)
        self.players.append(player1)

        # Only add second player if not in single-player mode
        if not getattr(config, 'SINGLEPLAYER_MODE', False):
            player2 = Player(13 * TILE_WIDTH, 13 * TILE_HEIGHT, player2_sprite)
            self.players.append(player2)

        # Flag to spawn initial beer powerups on first update
        self.initial_spawn_done = False

        # Load level music if specified
        self._load_level_music()

        # Spawn initial fence birds
        self._spawn_fence_birds()

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

        # Draw score display
        if getattr(config, 'SINGLEPLAYER_MODE', False):
            # Single-player mode: Show bird score
            ledwall.drawText(f'BIRDS: {self.bird_score}/{self.target_bird_score}', x=2, y=game_state.level.getHeight() * 2, color=(255, 255, 0))
        else:
            # Multiplayer mode: Show player scores
            ledwall.drawText(f'HITS: {self.players[0].score}', x=2, y=game_state.level.getHeight() * 2, color=(255, 255, 0))
            if len(self.players) > 1:
                ledwall.drawText(f'HITS: {self.players[1].score}', x=20, y=game_state.level.getHeight() * 2, color=(255, 255, 0))

        # Draw ammo display with color coding
        if getattr(config, 'DUCK_HUNT_MODE', False):
            # Duck Hunt mode: show unlimited ammo
            ledwall.drawText('AMMO: ∞', x=2, y=game_state.level.getHeight() * 2 + 1, color=(0, 255, 0))
        else:
            # Normal mode: show actual ammo count
            ammo1_color = (255, 255, 255) if self.players[0].ammo > 0 else (255, 0, 0)
            ledwall.drawText(f'AMMO: {self.players[0].ammo}', x=2, y=game_state.level.getHeight() * 2 + 1, color=ammo1_color)
        
        if not getattr(config, 'SINGLEPLAYER_MODE', False) and len(self.players) > 1:
            ammo2_color = (255, 255, 255) if self.players[1].ammo > 0 else (255, 0, 0)
            ledwall.drawText(f'AMMO: {self.players[1].ammo}', x=20, y=game_state.level.getHeight() * 2 + 1, color=ammo2_color)

        # Draw alcohol level display (nur wenn Alkohol aktiviert)
        if config.ALCOHOL_ENABLED and not getattr(config, 'SINGLEPLAYER_MODE', False):
            alcohol1_percent = int(self.players[0].alcohol_level * 100)

            # Color coding: green = sober, yellow = tipsy, red = drunk
            def get_alcohol_color(level):
                if level <= 20:
                    return (0, 255, 0)  # Green
                elif level <= 50:
                    return (255, 255, 0)  # Yellow
                else:
                    return (255, 0, 0)  # Red

            alcohol1_color = get_alcohol_color(alcohol1_percent)
            ledwall.drawText(f'ALC: {alcohol1_percent}%', x=2, y=game_state.level.getHeight() * 2 + 2, color=alcohol1_color)
            
            if len(self.players) > 1:
                alcohol2_percent = int(self.players[1].alcohol_level * 100)
                alcohol2_color = get_alcohol_color(alcohol2_percent)
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

        # Health-Position anpassen je nachdem ob Alkohol-HUD vorhanden ist
        alcohol_display_active = config.ALCOHOL_ENABLED and not getattr(config, 'SINGLEPLAYER_MODE', False)
        health_y_pos = game_state.level.getHeight() * 2 + (3 if alcohol_display_active else 2)
        ledwall.drawText(f'HP: {self.players[0].health}', x=2, y=health_y_pos, color=health1_color)
        
        if not getattr(config, 'SINGLEPLAYER_MODE', False) and len(self.players) > 1:
            health2_color = get_health_color(self.players[1].health)
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

            # Handle player controls
            player_keys = [controls.PLAYER_1_KEYS]
            if not getattr(config, 'SINGLEPLAYER_MODE', False):
                player_keys.append(controls.PLAYER_2_KEYS)
                
            for i, keys in enumerate(player_keys):
                if i >= len(self.players):
                    continue
                    
                if e.key == keys[controls.DIR_LEFT]:
                    self.players[i].moveLeft()
                elif e.key == keys[controls.DIR_RIGHT]:
                    self.players[i].moveRight()
                elif e.key == keys[controls.DIR_UP]:
                    self.players[i].moveUp()
                elif e.key == keys[controls.DIR_DOWN]:
                    self.players[i].moveDown()

                elif e.key == keys[controls.FIRE]:
                    if getattr(config, 'SINGLEPLAYER_MODE', False):
                        # In single-player mode, just shoot in facing direction
                        self.players[i].shoot(i)
                    else:
                        # In multiplayer mode, pass the other player's position to determine shooting direction
                        other_player_index = 1 - i  # Get the other player (0->1, 1->0)
                        other_player_x = self.players[other_player_index].xpos
                        self.players[i].shoot(i, other_player_x)

        elif e.type == pygame.KEYUP:
            # Handle player key releases
            player_keys = [controls.PLAYER_1_KEYS]
            if not getattr(config, 'SINGLEPLAYER_MODE', False):
                player_keys.append(controls.PLAYER_2_KEYS)
                
            for i, keys in enumerate(player_keys):
                if i >= len(self.players):
                    continue
                    
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
            actions = controls.handleJoyEvent(e)
            for action in actions:
                controls.performAction(action, self.players[e.instance_id], e.instance_id)

    def update(self):

        # Spawn initial beer powerups on first update
        if not self.initial_spawn_done:
            if config.ALCOHOL_ENABLED:
                self._spawn_initial_beer_powerups()
            self.initial_spawn_done = True

        for i, player in enumerate(self.players):
            # Update facing direction to look towards other player (only in multiplayer)
            if not getattr(config, 'SINGLEPLAYER_MODE', False) and len(self.players) > 1:
                other_player_index = 1 - i
                other_player_x = self.players[other_player_index].xpos
                player.update_facing_direction(other_player_x)

            player.update()
            
            # Check if a player just died and trigger bird circling
            if player.dying and not self.birds_circling:
                self._start_bird_circling(player.xpos, player.ypos)
        
        # Check if both players are no longer dying (respawned) and stop bird circling
        if self.birds_circling and not any(player.dying for player in self.players):
            self._stop_bird_circling()

        # Check if a player has won
        checkVictory()

        if game_state.message:  # do not handle rest of updates while message is shown
            game_state.message.update()
            
            # Allow bird updates to continue if they are circling
            if self.birds_circling:
                for obj in self.objects:
                    if isinstance(obj, (Bird, FenceBird)):
                        obj.update()
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

        # Spawn weapon drops periodically (only if not in Duck Hunt mode)
        if not getattr(config, 'DUCK_HUNT_MODE', False):
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

        # Spawn birds randomly
        self._handle_bird_spawning()

        # Occasionally respawn fence birds
        self._handle_fence_bird_respawn()

        # Remove expired powerups and inactive birds
        for obj in self.objects[:]:
            if isinstance(obj, (BeerPowerup, HealthPowerup)):
                if obj.update():  # Returns True if should be removed
                    self.removeObject(obj)
            elif isinstance(obj, (Bird, FenceBird)):
                if not obj.is_active():
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

            # Set Duck Hunt mode based on level metadata
            config.DUCK_HUNT_MODE = level_data.duck_hunt_mode

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
            self.bird_spawn_timer = 0
            self.initial_spawn_done = False

            # Spawn new fence birds for this level
            self._spawn_fence_birds()

            # Show level change message
            import game_state
            from message import Message
            game_state.message = Message(f"Level: {level_data.name}", 60)

            if config.DEBUG_MODE:
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

    def _handle_bird_spawning(self):
        """Handle random bird spawning across the screen."""
        self.bird_spawn_timer += 1

        # Different spawn intervals for single-player vs multiplayer
        if getattr(config, 'SINGLEPLAYER_MODE', False):
            # More frequent spawning in single-player mode (1-3 seconds)
            spawn_interval = random.randint(60, 180)
        else:
            # Normal spawning in multiplayer mode (3-10 seconds)
            spawn_interval = random.randint(180, 600)

        if self.bird_spawn_timer >= spawn_interval:
            # Count all birds (both flying and fence birds)
            flying_birds = [obj for obj in self.objects if isinstance(obj, Bird)]
            fence_birds = [obj for obj in self.objects if isinstance(obj, FenceBird)]
            total_birds = len(flying_birds) + len(fence_birds)
            
            # Different max bird limits for single-player vs multiplayer
            max_birds = 15 if getattr(config, 'SINGLEPLAYER_MODE', False) else 10
            
            # Only spawn if there aren't too many birds already
            # and birds aren't currently fleeing after a respawn
            if total_birds < max_birds and not self._birds_are_fleeing():
                self._spawn_random_bird()
            self.bird_spawn_timer = 0

    def _spawn_random_bird(self):
        """Spawn a bird at a random position flying across the screen."""
        # Random height within the game area (avoid UI area at bottom)
        screen_height = game_state.level.getHeight() * TILE_HEIGHT
        y = random.randint(16, screen_height - 32)  # Leave some margin

        # Randomly choose direction
        flying_right = random.choice([True, False])

        if flying_right:
            # Spawn from left edge, flying right
            x = -16  # Start just off screen
        else:
            # Spawn from right edge, flying left
            x = game_state.output.get_width()

        # Create the bird - it will adjust its own Y position if it has a landing target
        bird = Bird(x, y, flying_right)
        
        # If birds are circling, make this new bird start circling too (not in Duck Hunt mode)
        if self.birds_circling and not getattr(config, 'DUCK_HUNT_MODE', False):
            bird.start_circling(self.dead_player_x, self.dead_player_y)
            
        self.addObject(bird)

    def _load_level_music(self):
        """Load and play music for the current level if specified."""
        from level_loader import get_level_loader
        from sound_manager import play_music, stop_music
        
        try:
            level_loader = get_level_loader()
            current_level = level_loader.get_current_level()
            
            if current_level.music:
                play_music(current_level.music)
            else:
                stop_music()
        except Exception as e:
            print(f"Error loading level music: {e}")

    def _spawn_fence_birds(self):
        """Spawn birds on some fence and cactus tiles at game start."""
        if not hasattr(game_state, 'level') or not game_state.level:
            return

        perch_positions = []

        # Find all fence and cactus tiles
        for y in range(game_state.level.getHeight()):
            for x in range(game_state.level.getWidth()):
                tile = game_state.level.getTile(x, y)
                if tile in ['#', 'Y']:  # Fence or cactus
                    perch_positions.append((x, y, tile))

        # Randomly place birds on some perches (about 10-15% chance per tile)
        for x, y, tile_type in perch_positions:
            if random.random() < 0.12:  # 12% chance for a bird on each perch
                # Place bird on top of the tile
                fence_bird = FenceBird(x * TILE_WIDTH, y * TILE_HEIGHT - 4, x, y, tile_type)
                self.addObject(fence_bird)

    def _handle_fence_bird_respawn(self):
        """Occasionally respawn fence birds during gameplay."""
        # Only check every 10 seconds (600 frames)
        if game_state.tick % 600 == 0:
            # Count existing fence birds
            fence_birds = [obj for obj in self.objects if isinstance(obj, FenceBird)]

            # If we have fewer than 3 fence birds, maybe spawn one
            if len(fence_birds) < 3 and random.random() < 0.3:  # 30% chance
                self._spawn_single_fence_bird()

    def _spawn_single_fence_bird(self):
        """Spawn a single fence bird on a random empty fence or cactus."""
        if not hasattr(game_state, 'level') or not game_state.level:
            return

        # Find all fence and cactus positions
        perch_positions = []
        for y in range(game_state.level.getHeight()):
            for x in range(game_state.level.getWidth()):
                tile = game_state.level.getTile(x, y)
                if tile in ['#', 'Y']:  # Fence or cactus
                    perch_positions.append((x, y, tile))

        if not perch_positions:
            return

        # Check which perch positions don't already have birds
        empty_perches = []
        for fx, fy, tile_type in perch_positions:
            perch_x = fx * TILE_WIDTH
            perch_y = fy * TILE_HEIGHT - 4

            # Check if there's already a fence bird at this position
            has_bird = False
            for obj in self.objects:
                if isinstance(obj, FenceBird):
                    if abs(obj.xpos - perch_x) < 8 and abs(obj.ypos - perch_y) < 8:
                        has_bird = True
                        break

            if not has_bird:
                empty_perches.append((fx, fy, tile_type))

        # Spawn on a random empty perch
        if empty_perches:
            x, y, tile_type = random.choice(empty_perches)
            fence_bird = FenceBird(x * TILE_WIDTH, y * TILE_HEIGHT - 4, x, y, tile_type)
            self.addObject(fence_bird)
    
    def _start_bird_circling(self, dead_player_x, dead_player_y):
        """Start all birds circling around the dead player."""
        self.birds_circling = True
        self.dead_player_x = dead_player_x
        self.dead_player_y = dead_player_y
        
        # Make all existing birds start circling (not in Duck Hunt mode)
        if not getattr(config, 'DUCK_HUNT_MODE', False):
            for obj in self.objects:
                if isinstance(obj, (Bird, FenceBird)):
                    obj.start_circling(dead_player_x, dead_player_y)
    
    def _stop_bird_circling(self):
        """Stop bird circling and make all birds leave the map."""
        self.birds_circling = False
        
        # Play bird launch sound for mass exodus
        SFX_BIRD_LAUNCH.play()
        
        # Make all birds fly away off the map (not in Duck Hunt mode)
        if not getattr(config, 'DUCK_HUNT_MODE', False):
            for obj in self.objects[:]:  # Use slice to avoid modification during iteration
                if isinstance(obj, (Bird, FenceBird)):
                    obj.state = "scared_flying"
                    obj.flying_right = random.choice([True, False])
                    obj.flee_speed = random.uniform(2.0, 4.0)  # Faster exit speed
                    
                    # Convert to flying sprite if it's a fence bird
                    if isinstance(obj, FenceBird):
                        obj.sprite = createAnimatedSprite('gfx/birdfly1.png', 16, 16)
                        if obj.flying_right:
                            obj.sprite.select(1)  # Row 1 = flying right
                        else:
                            obj.sprite.select(0)  # Row 0 = flying left
                        obj.sprite.speed = 8
                        obj.sprite.start()
    
    def _birds_are_fleeing(self):
        """Check if birds are currently fleeing the map."""
        # Check if any birds are in scared_flying state (fleeing)
        for obj in self.objects:
            if isinstance(obj, (Bird, FenceBird)) and obj.state == "scared_flying":
                return True
        return False