"""
Game logic module for Drunk Duel.
Contains collision detection, weapon spawning, and other game mechanics.
"""

import random

import config
import controls
import ledwall
from bullet import Bullet
from message import Message
from weapon_drop import WeaponDrop
from beer_powerup import BeerPowerup
from health_powerup import HealthPowerup
from bird import Bird, FenceBird
from explosion import Explosion
from sound_manager import SFX_FOOTSTEP, SFX_LAUGHING, SFX_PLAYER_HIT, SFX_RELOAD
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState

# Override print function
import ledwall
print = ledwall.print


def is_tile_spawnable(x, y):
    """Check if a tile position is suitable for spawning items, cacti, etc."""
    if not game_state.level:
        return False
    
    if x < 0 or x >= game_state.level.getWidth() or y < 0 or y >= game_state.level.getHeight():
        return False
    
    tile = game_state.level.getTile(x, y)
    # Only allow spawning on empty space, not on no-spawn zones (N) or other tiles
    return tile == ' '


def spawnBullet(x, y, xdir, shooter_index, bullet_sprite, ydir=0):
    """Spawn a bullet at the given position."""

    bullet = Bullet(x, y, bullet_sprite)
    bullet.xdir = xdir
    bullet.ydir = ydir  # Add vertical direction support
    bullet.shooter_index = shooter_index

    # Set damage modifier based on shooter's alcohol level
    shooter = game_state.gameScreen.players[shooter_index]
    bullet.drunk_damage_modifier = shooter.get_drunk_damage_modifier()

    game_state.gameScreen.addObject(bullet)


def spawnBeerPowerup(beer_sprite):
    """Spawn a beer powerup at a random empty location."""
    # Nur wenn Alkohol aktiviert ist
    if not config.ALCOHOL_ENABLED:
        return

    for attempt in range(50):  # Versuche maximal 50 mal einen freien Platz zu finden
        x = random.randint(1, 14)  # Avoid edges
        y = random.randint(1, 14)

        # Check if position is empty and not a no-spawn zone
        if is_tile_spawnable(x, y):
            beer_powerup = BeerPowerup(x * TILE_WIDTH, y * TILE_HEIGHT, beer_sprite)
            game_state.gameScreen.addObject(beer_powerup)
            return
def spawnHealthPowerup(health_sprite):
    """Spawn a health powerup at a random empty location."""
    # Find a random empty spot on the map
    attempts = 0
    while attempts < 100:  # Prevent infinite loop
        x = random.randint(0, game_state.level.getWidth() - 1)
        y = random.randint(0, game_state.level.getHeight() - 1)

        if is_tile_spawnable(x, y):  # Empty space (not no-spawn zone)
            health_powerup = HealthPowerup(x * TILE_WIDTH, y * TILE_HEIGHT, health_sprite)
            game_state.gameScreen.addObject(health_powerup)
            if config.DEBUG_MODE:
                print(f"Medkit gespawnt bei Position ({x}, {y})")  # Debug-Ausgabe
            break
        attempts += 1


def checkHealthPickup():
    """Check if players pick up health powerups."""
    for health in game_state.gameScreen.objects[:]:
        if isinstance(health, HealthPowerup):
            for player in game_state.gameScreen.players:
                # Check collision with player
                if (health.xpos < player.xpos + TILE_WIDTH and
                    health.xpos + TILE_WIDTH > player.xpos and
                    health.ypos < player.ypos + TILE_HEIGHT and
                    health.ypos + TILE_HEIGHT > player.ypos):

                    # Player heilt sich
                    old_health = player.health
                    player.heal(health.get_health_amount())
                    healed_amount = player.health - old_health

                    if config.DEBUG_MODE:
                        print(f"Player {game_state.gameScreen.players.index(player) + 1} healed {healed_amount} HP")

                    # Remove the health powerup
                    game_state.gameScreen.removeObject(health)

                    # Play pickup sound
                    SFX_FOOTSTEP.play()
                    break
    """Check if players pick up beer powerups."""
    for beer in game_state.gameScreen.objects[:]:
        if isinstance(beer, BeerPowerup):
            for player in game_state.gameScreen.players:
                # Check collision with player
                if (beer.xpos < player.xpos + TILE_WIDTH and
                    beer.xpos + TILE_WIDTH > player.xpos and
                    beer.ypos < player.ypos + TILE_HEIGHT and
                    beer.ypos + TILE_HEIGHT > player.ypos):

                    # Player trinkt Bier
                    player.drin(beer.get_alcohol_amount())

                    # Remove the beer powerup
                    game_state.gameScreen.removeObject(beer)
                    break


def spawnWeaponDrop(munition_sprite):
    """Spawn a weapon drop at a random empty location."""
    # Find a random empty spot on the map
    attempts = 0
    while attempts < 100:  # Prevent infinite loop
        x = random.randint(0, game_state.level.getWidth() - 1)
        y = random.randint(0, game_state.level.getHeight() - 1)

        if is_tile_spawnable(x, y):  # Empty space (not no-spawn zone)
            weapon_drop = WeaponDrop(x * TILE_WIDTH, y * TILE_HEIGHT, munition_sprite)
            game_state.gameScreen.addObject(weapon_drop)
            break
        attempts += 1


def checkWeaponPickup():
    """Check if players pick up weapon drops."""
    for weapon_drop in game_state.gameScreen.objects[:]:
        if isinstance(weapon_drop, WeaponDrop):
            for player in game_state.gameScreen.players:
                # Check collision with player
                if (weapon_drop.xpos < player.xpos + TILE_WIDTH and
                    weapon_drop.xpos + TILE_WIDTH > player.xpos and
                    weapon_drop.ypos < player.ypos + TILE_HEIGHT and
                    weapon_drop.ypos + TILE_HEIGHT > player.ypos):

                    # Player picks up ammo
                    player.ammo = min(player.ammo + weapon_drop.ammo_amount, 10)  # Max 10 ammo

                    # Remove the weapon drop
                    game_state.gameScreen.removeObject(weapon_drop)

                    # Play pickup sound (reuse footstep for now)
                    SFX_RELOAD.play()
                    break


def checkBeerPickup():
    """Check if players pick up beer powerups."""
    # Nur wenn Alkohol aktiviert ist
    if not config.ALCOHOL_ENABLED:
        return

    for beer in game_state.gameScreen.objects[:]:
        if isinstance(beer, BeerPowerup):
            for player in game_state.gameScreen.players:
                # Check collision with player
                if (beer.xpos < player.xpos + TILE_WIDTH and
                    beer.xpos + TILE_WIDTH > player.xpos and
                    beer.ypos < player.ypos + TILE_HEIGHT and
                    beer.ypos + TILE_HEIGHT > player.ypos):

                    # Player trinkt Bier
                    player.drink_alcohol(beer.get_alcohol_amount())

                    # Remove the beer powerup
                    game_state.gameScreen.removeObject(beer)

                    # Play random laughing sound
                    random.choice(SFX_LAUGHING).play()

                    break


def checkFallingBirdCollisions():
    """Check if falling birds hit players and cause damage."""
    for bird in game_state.gameScreen.objects[:]:  # Use slice to avoid modification during iteration
        if ((isinstance(bird, Bird) and bird.state == "falling") or 
            (isinstance(bird, FenceBird) and bird.state == "falling")):
            
            bird_bounds = bird.get_bounds()
            
            # Check collision with each player
            for i, player in enumerate(game_state.gameScreen.players):
                if player.dying:
                    continue
                    
                # Simple bounding box collision detection
                if (bird_bounds['x'] < player.xpos + TILE_WIDTH and
                    bird_bounds['x'] + bird_bounds['width'] > player.xpos and
                    bird_bounds['y'] < player.ypos + TILE_HEIGHT and
                    bird_bounds['y'] + bird_bounds['height'] > player.ypos):

                    # Bird hit player!
                    _handle_falling_bird_hit(bird, i)
                    break  # Bird can only hit one player


def _handle_falling_bird_hit(bird, hit_player_index):
    """Handle when a falling bird hits a player."""
    hit_player = game_state.gameScreen.players[hit_player_index]

    if hit_player.dying:
        return

    # Bird damage (less than bullet damage)
    bird_damage = 15  # Fixed damage for bird hits
    is_dead = hit_player.take_damage(bird_damage)

    # Remove bird immediately to prevent further collisions
    bird.active = False
    game_state.gameScreen.removeObject(bird)
    
    # Play sound effect
    SFX_PLAYER_HIT.play()

    # Create explosion at bird's position
    explosion = Explosion(bird.xpos, bird.ypos)
    game_state.gameScreen.addObject(explosion)

    # Only kill player if they actually died from the damage
    if is_dead:
        # Reset hit player position
        player = game_state.gameScreen.players[hit_player_index]
        player.die()

        # Make player stop moving
        for player in game_state.gameScreen.players:
            player.stopMoving()


def checkCollisions():
    """Check bullet-player and bullet-bird collisions and handle hits."""
    # Check for falling bird-player collisions
    checkFallingBirdCollisions()
    
    for bullet in game_state.gameScreen.objects[:]:  # Use slice to avoid modification during iteration
        if isinstance(bullet, Bullet):
            bullet_hit = False

            # Check bullet-player collisions
            for i, player in enumerate(game_state.gameScreen.players):
                # Skip collision check with the player who shot the bullet
                if i == bullet.shooter_index:
                    continue

                # Simple bounding box collision detection
                if (bullet.xpos < player.xpos + TILE_WIDTH // 2 and
                    bullet.xpos + TILE_WIDTH // 2 > player.xpos and
                    bullet.ypos < player.ypos + TILE_HEIGHT // 2 and
                    bullet.ypos + TILE_HEIGHT // 2 > player.ypos):

                    _handle_player_hit(bullet, i)
                    bullet_hit = True
                    break

            # Check bullet-bird collisions (only if bullet didn't hit a player)
            if not bullet_hit:
                for bird in game_state.gameScreen.objects[:]:
                    if isinstance(bird, Bird) and bird.state in ["flying", "landing"]:
                        bird_bounds = bird.get_bounds()

                        # Simple bounding box collision detection
                        if (bullet.xpos < bird_bounds['x'] + bird_bounds['width'] and
                            bullet.xpos + TILE_WIDTH > bird_bounds['x'] and
                            bullet.ypos < bird_bounds['y'] + bird_bounds['height'] and
                            bullet.ypos + TILE_HEIGHT > bird_bounds['y']):

                            # Bird got hit!
                            bird.get_shot()
                            game_state.gameScreen.removeObject(bullet)
                            _handle_bird_hit()
                            bullet_hit = True
                            break
                    elif isinstance(bird, FenceBird) and bird.state in ["sitting", "scared_flying"]:
                        bird_bounds = bird.get_bounds()

                        # Simple bounding box collision detection
                        if (bullet.xpos < bird_bounds['x'] + bird_bounds['width'] and
                            bullet.xpos + TILE_WIDTH > bird_bounds['x'] and
                            bullet.ypos < bird_bounds['y'] + bird_bounds['height'] and
                            bullet.ypos + TILE_HEIGHT > bird_bounds['y']):

                            # Fence bird got hit!
                            bird.get_shot()
                            game_state.gameScreen.removeObject(bullet)
                            _handle_bird_hit()
                            bullet_hit = True
                            break

            # Check bullet-weapon drop collisions (only if bullet didn't hit anything else)
            if not bullet_hit:
                for weapon_drop in game_state.gameScreen.objects[:]:
                    if isinstance(weapon_drop, WeaponDrop):
                        weapon_bounds = weapon_drop.get_bounds()

                        # Simple bounding box collision detection
                        if (bullet.xpos < weapon_bounds['x'] + weapon_bounds['width'] and
                            bullet.xpos + TILE_WIDTH > weapon_bounds['x'] and
                            bullet.ypos < weapon_bounds['y'] + weapon_bounds['height'] and
                            bullet.ypos + TILE_HEIGHT > weapon_bounds['y']):

                            # Weapon drop got hit - explode it!
                            weapon_drop.get_hit()
                            game_state.gameScreen.removeObject(bullet)
                            bullet_hit = True
                            break


def _handle_bird_hit():
    """Handle when a bird gets hit by a bullet in single-player mode."""
    if getattr(config, 'SINGLEPLAYER_MODE', False):
        # Award points for hitting birds in single-player mode
        game_state.gameScreen.bird_score += 1


def _handle_player_hit(bullet, hit_player_index):
    """Handle when a player gets hit by a bullet."""
    hit_player = game_state.gameScreen.players[hit_player_index]

    if hit_player.dying:
        return

    other_player_index = 1 - hit_player_index
    other_player = game_state.gameScreen.players[other_player_index]

    # Calculate damage from bullet
    damage = bullet.get_total_damage()
    is_dead = hit_player.take_damage(damage)

    # Remove bullet and play sound effect
    game_state.gameScreen.removeObject(bullet)
    SFX_PLAYER_HIT.play()

    # Only kill player if they actually died from the damage
    if is_dead:
        # Award point to the shooter only on death
        other_player.score += 1

        # Reset hit player position
        player = game_state.gameScreen.players[hit_player_index]
        player.die()

        # Switch controls only on death
        # and only if not victory yet (HACK)
        if game_state.gameScreen.players[bullet.shooter_index].score < config.WIN_SCORE:
            randomizeControls(bullet.shooter_index)

        for player in game_state.gameScreen.players:
            player.stopMoving()


def removeAllBullets():
    """Remove all bullets from the game."""
    bullets_to_remove = []
    for obj in game_state.gameScreen.objects:
        if isinstance(obj, Bullet):
            bullets_to_remove.append(obj)

    for bullet in bullets_to_remove:
        game_state.gameScreen.removeObject(bullet)


def _load_next_duckhunt_level():
    """Load the next duckhunt level and reset game state."""
    from level_loader import get_level_loader
    from level import Level
    from message import Message
    
    level_loader = get_level_loader()
    current_level_data = level_loader.get_current_level()
    
    # Create new level with the new data
    game_state.level = Level(current_level_data.mapdata, game_state.level.tiles)
    
    # Set Duck Hunt mode based on level metadata
    config.DUCK_HUNT_MODE = current_level_data.duck_hunt_mode
    
    # Reset game state for new level (but keep accumulated bird score)
    previous_bird_score = game_state.gameScreen.bird_score
    game_state.gameScreen.bird_score = previous_bird_score  # Keep total score across levels
    game_state.gameScreen.target_bird_score = previous_bird_score + 20  # Increase target for next level
    
    # Reset player position to bottom center of new map
    from game_state import TILE_WIDTH, TILE_HEIGHT
    duck_hunt_x = (game_state.level.getWidth() // 2) * TILE_WIDTH
    duck_hunt_y = (game_state.level.getHeight() - 2) * TILE_HEIGHT
    game_state.gameScreen.players[0].xpos = duck_hunt_x
    game_state.gameScreen.players[0].ypos = duck_hunt_y
    
    # Reset player health and state
    game_state.gameScreen.players[0].health = game_state.gameScreen.players[0].max_health
    game_state.gameScreen.players[0].dying = False
    
    # Clear all objects except player
    new_objects = [obj for obj in game_state.gameScreen.objects if obj in game_state.gameScreen.players]
    game_state.gameScreen.objects = new_objects
    
    # Load level music if specified
    from sound_manager import play_music, stop_music
    if current_level_data.music:
        play_music(current_level_data.music)
    else:
        stop_music()
    
    # Show level transition message
    level_name = current_level_data.name.upper()
    level_number = level_loader.current_level_index + 1
    game_state.message = Message(0, 0, ['', 'level', str(level_number), level_name], (255, 255, 0), 90)
    
    if config.DEBUG_MODE:
        print(f"Advanced to Duck Hunt level: {current_level_data.name}")


def checkVictory():
    # First check if one of the players is dead:
    for player in game_state.gameScreen.players:
        if player.dying:
            if player.sprite.lastPhase < 3:
                return

    # Check for victory condition
    if getattr(config, 'SINGLEPLAYER_MODE', False):
        # Single-player mode: check bird score
        if game_state.gameScreen.bird_score >= game_state.gameScreen.target_bird_score:
            # Check if this is Duck Hunt mode
            if getattr(config, 'DUCK_HUNT_MODE', False):
                # Duck Hunt mode: advance to next level
                from level_loader import get_level_loader
                level_loader = get_level_loader()
                
                # Get current level index to check if there are more levels
                current_index = level_loader.current_level_index
                total_levels = level_loader.get_level_count()
                
                if current_index < total_levels - 1:
                    # More levels available - advance to next level
                    level_loader.next_level()
                    _load_next_duckhunt_level()
                else:
                    # No more levels - show victory screen
                    game_state.gameScreen.winner = 0  # Player 1 wins in single-player
                    switchState('gameover')
            else:
                # Regular single-player mode
                game_state.gameScreen.winner = 0  # Player 1 wins in single-player
                switchState('gameover')
    else:
        # Multiplayer mode: check player scores (first to 5 points wins)
        for player in game_state.gameScreen.players:
            if player.score >= config.WIN_SCORE:
                game_state.gameScreen.winner = game_state.gameScreen.players.index(player)
                switchState('gameover')


def randomizeControls(playerid):
    controls.restore(playerid)
    keymapping = [controls.PLAYER_1_KEYS, controls.PLAYER_2_KEYS][playerid]
    orig, repl = controls.swapRandomly(keymapping)

    message1 = 'spieler %s:' % (playerid + 1)
    message2 = controls.getSentence(orig, repl)

    if playerid == 0:
        x = 2
        color = (255, 255, 0)
    else:
        x = 19
        color = (0, 255, 0)

    y = 8

    message = Message(x, y, ['', 'spieler', ['eins', 'zwei'][playerid], '', *message2], color)
    game_state.message = message
