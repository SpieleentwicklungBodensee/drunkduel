"""
Game logic module for Drunk Duel.
Contains collision detection, weapon spawning, and other game mechanics.
"""

import random

import controls
import ledwall
from bullet import Bullet
from message import Message
from weapon_drop import WeaponDrop
from sound_manager import SFX_FOOTSTEP, SFX_PLAYER_HIT
import game_state
from game_state import TILE_WIDTH, TILE_HEIGHT, switchState

def spawnBullet(x, y, xdir, shooter_index, bullet_sprite):
    """Spawn a bullet at the given position."""

    bullet = Bullet(x, y, bullet_sprite)
    bullet.xdir = xdir
    bullet.shooter_index = shooter_index
    game_state.gameScreen.addObject(bullet)


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
        game_state.gameScreen.players[other_player_index].ammo + 2, 6)

    # Remove bullet and play sound effect
    game_state.gameScreen.removeObject(bullet)
    SFX_PLAYER_HIT.play()

    # Reset hit player position
    player = game_state.gameScreen.players[hit_player_index]
    if hit_player_index == 0:  # Player 1 hit
        player.xpos = 2 * TILE_WIDTH
        player.ypos = 2 * TILE_HEIGHT
    else:  # Player 2 hit
        player.xpos = 13 * TILE_WIDTH
        player.ypos = 13 * TILE_HEIGHT

    # Reset ammo for hit player
    player.ammo = 4

    # Check for victory condition (first to 5 points wins)
    if game_state.gameScreen.players[other_player_index].score >= 5:
        game_state.gameScreen.winner = other_player_index + 1
        switchState('gameover')

    # Switch controls
    randomizeControls(bullet.shooter_index)


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
