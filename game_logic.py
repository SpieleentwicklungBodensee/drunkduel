"""
Game logic module for Drunk Duel.
Contains collision detection, weapon spawning, and other game mechanics.
"""

import random

import controls
import config
from bullet import Bullet
from message import Message
from weapon_drop import WeaponDrop
from beer_powerup import BeerPowerup
from sound_manager import SFX_FOOTSTEP, SFX_PLAYER_HIT, SFX_BEER_PICKUP
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState

def spawnBullet(x, y, xdir, shooter_index, bullet_sprite):
    """Spawn a bullet at the given position."""

    bullet = Bullet(x, y, bullet_sprite)
    bullet.xdir = xdir
    bullet.shooter_index = shooter_index
    game_state.gameScreen.addObject(bullet)


def spawnBeerPowerup(beer_sprite):
    """Spawn a beer powerup at a random empty location."""
    # Find a random empty spot on the map
    attempts = 0
    while attempts < 100:  # Prevent infinite loop
        x = random.randint(0, game_state.level.getWidth() - 1)
        y = random.randint(0, game_state.level.getHeight() - 1)

        if game_state.level.getTile(x, y) == ' ':  # Empty space
            beer_powerup = BeerPowerup(x * TILE_WIDTH, y * TILE_HEIGHT, beer_sprite)
            game_state.gameScreen.addObject(beer_powerup)
            print(f"Bier gespawnt bei Position ({x}, {y})")  # Debug-Ausgabe
            break
        attempts += 1


def checkBeerPickup():
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
                    player.drink_alcohol(beer.get_alcohol_amount())

                    # Remove the beer powerup
                    game_state.gameScreen.removeObject(beer)

                    # Play pickup sound (reuse footstep for now)
                    SFX_FOOTSTEP.play()
                    break


def spawnWeaponDrop(munition_sprite):
    """Spawn a weapon drop at a random empty location."""
    # Find a random empty spot on the map
    attempts = 0
    while attempts < 100:  # Prevent infinite loop
        x = random.randint(0, game_state.level.getWidth() - 1)
        y = random.randint(0, game_state.level.getHeight() - 1)

        if game_state.level.getTile(x, y) == ' ':  # Empty space
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
                    SFX_FOOTSTEP.play()
                    break


def checkBeerPickup():
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
                    player.drink_alcohol(beer.get_alcohol_amount())

                    # Remove the beer powerup
                    game_state.gameScreen.removeObject(beer)

                    # Play beer pickup sound
                    SFX_BEER_PICKUP.play()
                    break


def checkCollisions():
    """Check bullet-player collisions and handle hits."""
    for bullet in game_state.gameScreen.objects[:]:  # Use slice to avoid modification during iteration
        if isinstance(bullet, Bullet):
            for i, player in enumerate(game_state.gameScreen.players):
                # Skip collision check with the player who shot the bullet
                if i == bullet.shooter_index:
                    continue

                # Simple bounding box collision detection
                if (bullet.xpos < player.xpos + TILE_WIDTH and
                    bullet.xpos + TILE_WIDTH > player.xpos and
                    bullet.ypos < player.ypos + TILE_HEIGHT and
                    bullet.ypos + TILE_HEIGHT > player.ypos):

                    _handle_player_hit(bullet, i)
                    break


def _handle_player_hit(bullet, hit_player_index):
    """Handle when a player gets hit by a bullet."""
    # Collision detected - increase score for the other player
    other_player_index = 1 - hit_player_index
    game_state.gameScreen.players[other_player_index].score += 1

    # Give shooter some ammo back as reward
    game_state.gameScreen.players[other_player_index].ammo = min(
        game_state.gameScreen.players[other_player_index].ammo + config.REWARD_AMMO, 6)

    # Remove bullet and play sound effect
    game_state.gameScreen.removeObject(bullet)
    SFX_PLAYER_HIT.play()

    # Reset hit player position
    player = game_state.gameScreen.players[hit_player_index]
    player.die()

    # Switch controls
    randomizeControls(bullet.shooter_index)
    for player in game_state.gameScreen.players:
        player.stopMoving()


def checkVictory():
    # Check for victory condition (first to 5 points wins)
    for player in game_state.gameScreen.players:
        if player.score >= 5:
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

    message = Message(x, y, [message1, *message2], color)
    game_state.message = message
