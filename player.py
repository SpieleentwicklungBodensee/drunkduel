
"""
Player class and related functionality for Drunk Duel.
Handles player movement, collision detection, and interactions.
"""
import controls
import random
import math
import config
import pygame
import game_state
from object import Object
from sprite import createAnimatedSprite
from game_logic import spawnBullet
from sound_manager import playFootstepSound, SFX_GUNSHOT, SFX_VOMIT, SFX_NOAMMO
from game_state import TILE_WIDTH, TILE_HEIGHT

# Override print function
import ledwall
print = ledwall.print


# Load player sprites
PLAYER_1_SPRITE = None
PLAYER_2_SPRITE = None


def load_player_sprites():
    """Load player sprites if not already loaded."""
    global PLAYER_1_SPRITE, PLAYER_2_SPRITE
    if PLAYER_1_SPRITE is None:
        PLAYER_1_SPRITE = createAnimatedSprite('gfx/player1.png')
    if PLAYER_2_SPRITE is None:
        PLAYER_2_SPRITE = createAnimatedSprite('gfx/player2.png')
    return PLAYER_1_SPRITE, PLAYER_2_SPRITE

class Player(Object):
    def __init__(self, xpos, ypos, sprite):
        super().__init__(xpos, ypos, sprite)

        self.xdir = 0
        self.ydir = 0
        self.speed = 1.5

        self.facedir = controls.DIR_DOWN

        self.score = 0
        self.ammo = 4
        self.showGun = False

        self.dying = False
        self.dyingTime = 0

        # Gesundheitssystem
        self.health = 100  # Maximale Gesundheit
        self.max_health = 100

        # Alkohol-System
        self.alcohol_level = 0.0  # 0.0 = nüchtern, 1.0 = sehr betrunken
        self.max_alcohol = 1.0
        self.alcohol_decay_rate = 0.0005  # Langsamerer Alkohol-Abbau (war 0.002)
        self.drunk_wobble_timer = 0  # Timer für Torkelbewegung
        self.drunk_vision_offset_x = 0  # Visuelle Verzerrung
        self.drunk_vision_offset_y = 0
        self.last_hiccup_time = 0  # Für Hickser-Sound-Timing
        self.random_movement_timer = 0  # Timer für zufällige Bewegungen

        # Ausnüchtern/Kotzen-System
        self.was_drunk = False  # War der Spieler betrunken?
        self.is_vomiting = False  # Kotzt der Spieler gerade?
        self.vomit_timer = 0  # Timer für Kotz-Animation
        self.vomit_duration = 120  # Dauer des Kotzens in Frames (2 Sekunden bei 60 FPS)
        self.last_vomit_time = 0  # Verhindert mehrfaches Kotzen

    def moveLeft(self):
        self.xdir = -1
        self.ydir = 0
        self.facedir = controls.DIR_LEFT

    def moveRight(self):
        self.xdir = 1
        self.ydir = 0
        self.facedir = controls.DIR_RIGHT

    def moveUp(self):
        # Prevent vertical movement in Duck Hunt mode
        if getattr(config, 'DUCK_HUNT_MODE', False):
            return
        self.xdir = 0
        self.ydir = -1
        self.facedir = controls.DIR_UP

    def moveDown(self):
        # Prevent vertical movement in Duck Hunt mode
        if getattr(config, 'DUCK_HUNT_MODE', False):
            return
        self.xdir = 0
        self.ydir = 1
        self.facedir = controls.DIR_DOWN

    def stopLeft(self):
        if self.xdir < 0:
            self.xdir = 0

    def stopRight(self):
        if self.xdir > 0:
            self.xdir = 0

    def stopUp(self):
        if self.ydir < 0:
            self.ydir = 0

    def stopDown(self):
        if self.ydir > 0:
            self.ydir = 0

    def stopMoving(self):
        """Stoppt alle Bewegungen des Spielers."""
        self.xdir = 0
        self.ydir = 0

    def shoot(self, player_index, other_player_x=None, other_player_y=None):
        # In Duck Hunt mode, player has unlimited ammo
        if not getattr(config, 'DUCK_HUNT_MODE', False):
            if self.ammo <= 0:
                SFX_NOAMMO.play()
                return  # Can't shoot without ammo
            self.ammo -= 1

        self.showGun = True

        # Alkohol beeinflusst die Schussrichtung
        accuracy_modifier = self.get_drunk_accuracy_modifier()

        # Check if Duck Hunt mode is enabled
        if getattr(config, 'DUCK_HUNT_MODE', False):
            # Duck Hunt mode: only shoot upward
            bulletxdir = 0
            bulletydir = -1  # Shoot upward
            self.facedir = controls.DIR_UP
        else:
            # Check if up/down shooting is enabled for this level
            from level_loader import get_level_loader
            level_loader = get_level_loader()
            current_level = level_loader.get_current_level()
            allow_up_down_shoot = current_level.allow_up_down_shoot
            
            # Normal shooting mode
            bulletydir = 0
            bulletxdir = 0
            
            # Determine shooting direction based on other player's position
            if other_player_x is not None and other_player_y is not None and allow_up_down_shoot:
                # Quadrant-based shooting: determine direction based on position relative to other player
                dx = other_player_x - self.xpos
                dy = other_player_y - self.ypos
                
                # Calculate which quadrant the other player is in relative to this player
                # Use absolute values to determine primary direction
                abs_dx = abs(dx)
                abs_dy = abs(dy)
                
                if abs_dx > abs_dy:
                    # Horizontal direction is primary
                    if dx > 0:
                        bulletxdir = 1  # Shoot right
                        self.facedir = controls.DIR_RIGHT
                    else:
                        bulletxdir = -1  # Shoot left
                        self.facedir = controls.DIR_LEFT
                    bulletydir = 0
                else:
                    # Vertical direction is primary
                    if dy > 0:
                        bulletydir = 1  # Shoot down
                        self.facedir = controls.DIR_DOWN
                    else:
                        bulletydir = -1  # Shoot up
                        self.facedir = controls.DIR_UP
                    bulletxdir = 0
                    
            elif other_player_x is not None:
                # Fallback to horizontal-only shooting (original behavior)
                if self.xpos < other_player_x:
                    bulletxdir = 1  # Shoot right
                    self.facedir = controls.DIR_RIGHT
                elif self.xpos > other_player_x:
                    bulletxdir = -1  # Shoot left
                    self.facedir = controls.DIR_LEFT
                else:
                    # Players are at same x position, use fallback direction
                    # Favor right direction as default
                    bulletxdir = 1
                    self.facedir = controls.DIR_RIGHT
            else:
                # Fallback: use old logic (position-based)
                if self.xpos < 128:
                    bulletxdir = 1
                    self.facedir = controls.DIR_RIGHT
                else:
                    bulletxdir = -1
                    self.facedir = controls.DIR_LEFT

            # Bei Betrunkenheit: zufällige Abweichung der Schussrichtung (only in normal mode)
            if accuracy_modifier < 1.0:
                if random.random() > accuracy_modifier:
                    # Schuss geht in zufällige Richtung
                    if allow_up_down_shoot:
                        # Allow random directions in all 4 directions
                        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down
                        random_dir = random.choice(directions)
                        bulletxdir = random_dir[0]
                        bulletydir = random_dir[1]
                    else:
                        # Only horizontal directions
                        directions = [-1, 1]
                        bulletxdir = random.choice(directions)
                        bulletydir = 0

        # Get bullet sprite from game state
        import game_state
        if hasattr(game_state, 'bullet_sprite'):
            bullet_sprite = game_state.bullet_sprite
        else:
            # Fallback: load directly
            from sprite import Sprite
            bullet_sprite = Sprite('gfx/bullet.png')

        spawnBullet(self.xpos, self.ypos, bulletxdir, player_index, bullet_sprite, bulletydir)
        SFX_GUNSHOT.play(loops=0)

    def stopShooting(self):
        self.showGun = False

    def update_facing_direction(self, other_player_x):
        """Update the facing direction to look towards the other player."""
        if not self.showGun:  # Only update when not actively shooting
            if self.xpos < other_player_x:
                self.facedir = controls.DIR_RIGHT
            elif self.xpos > other_player_x:
                self.facedir = controls.DIR_LEFT
            # If same x position, keep current direction

    def die(self):
        import game_state
        from game_logic import removeAllBullets

        # Remove all bullets when a player dies
        removeAllBullets()

        self.dying = True
        self.dyingTime = game_state.tick

        # set sprite animation
        self.sprite.select(8 + (1 if self.facedir == controls.DIR_LEFT else 0))
        self.sprite.speed = 12
        self.sprite.start(True)
        
        # In Duck Hunt mode, player death means game over
        if getattr(config, 'DUCK_HUNT_MODE', False):
            game_state.gameScreen.winner = -1  # No winner, just game over
            from game_state import switchState
            switchState('gameover')

    def drink_alcohol(self, amount=0.3):
        """Spieler trinkt Alkohol und wird betrunkener."""
        # Nur wenn Alkohol aktiviert ist
        if config.ALCOHOL_ENABLED:
            self.alcohol_level = min(self.max_alcohol, self.alcohol_level + amount)

    def get_drunk_level(self):
        """Gibt den Betrunkenheitsgrad zurück (0-4)."""
        if self.alcohol_level <= 0.2:
            return 0  # Nüchtern
        elif self.alcohol_level <= 0.4:
            return 1  # Leicht angetrunken
        elif self.alcohol_level <= 0.6:
            return 2  # Betrunken
        elif self.alcohol_level <= 0.8:
            return 3  # Stark betrunken
        else:
            return 4  # Völlig besoffen

    def get_drunk_speed_modifier(self):
        """Berechnet Geschwindigkeitsmodifikator basierend auf Alkohol-Level."""
        # Wenn Alkohol deaktiviert ist, immer normale Geschwindigkeit
        if not config.ALCOHOL_ENABLED:
            return 1.0

        drunk_level = self.get_drunk_level()
        if drunk_level == 0:
            return 1.0  # Normale Geschwindigkeit
        elif drunk_level == 1:
            return 0.9  # 10% langsamer
        elif drunk_level == 2:
            return 0.75  # 25% langsamer
        elif drunk_level == 3:
            return 0.6  # 40% langsamer
        else:
            return 0.4  # 60% langsamer

    def get_drunk_accuracy_modifier(self):
        """Berechnet Zielgenauigkeits-Modifier."""
        # Wenn Alkohol deaktiviert ist, immer normale Genauigkeit
        if not config.ALCOHOL_ENABLED:
            return 1.0

        drunk_level = self.get_drunk_level()
        if drunk_level <= 1:
            return 1.0
        elif drunk_level == 2:
            return 0.8
        elif drunk_level == 3:
            return 0.6
        else:
            return 0.3

    def get_drunk_damage_modifier(self):
        """Berechnet Schadens-Modifier für betrunkene Schüsse."""
        drunk_level = self.get_drunk_level()
        if drunk_level == 0:
            return 1.0  # Normaler Schaden
        elif drunk_level == 1:
            return 1.2  # +20% Schaden
        elif drunk_level == 2:
            return 1.5  # +50% Schaden
        elif drunk_level == 3:
            return 1.8  # +80% Schaden
        else:
            return 2.0  # +100% Schaden (doppelter Schaden)

    def take_damage(self, damage):
        """Spieler nimmt Schaden."""
        self.health -= damage
        if self.health < 0:
            self.health = 0
        return self.health <= 0  # Gibt True zurück wenn Spieler tot ist

    def heal(self, amount):
        """Heilt den Spieler."""
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self):
        """Prüft ob der Spieler noch am Leben ist."""
        return self.health > 0

    def reset_health(self):
        """Setzt die Gesundheit zurück."""
        self.health = self.max_health

    def start_vomiting(self):
        """Startet das Kotzen wenn der Spieler ausnüchtert."""
        import game_state

        # Verhindere mehrfaches Kotzen in kurzer Zeit
        if game_state.tick - self.last_vomit_time < 300:  # 5 Sekunden Cooldown
            return

        self.is_vomiting = True
        self.vomit_timer = self.vomit_duration
        self.last_vomit_time = game_state.tick

        # Spieler kann sich während dem Kotzen nicht bewegen
        self.xdir = 0
        self.ydir = 0

        # Spiele Kotz-Sound ab
        SFX_VOMIT.play()

        if config.DEBUG_MODE:
            print(f"Player {id(self)} kotzt! 🤮")  # Debug-Ausgabe

    def update_vomiting(self):
        """Aktualisiert das Kotz-System."""
        if self.is_vomiting:
            self.vomit_timer -= 1

            # Während dem Kotzen kann sich der Spieler nicht bewegen
            if self.vomit_timer > 0:
                self.xdir = 0
                self.ydir = 0

                # Kotz-Animation: leichtes Zittern
                if self.vomit_timer % 4 == 0:  # Alle 4 Frames
                    self.drunk_vision_offset_x = random.uniform(-0.5, 0.5)
                    self.drunk_vision_offset_y = random.uniform(-0.5, 0.5)
            else:
                # Kotzen ist vorbei
                self.is_vomiting = False
                self.drunk_vision_offset_x = 0
                self.drunk_vision_offset_y = 0

    def check_sobering_up(self):
        """Prüft ob der Spieler ausnüchtert und kotzen muss."""
        current_alcohol_percent = self.alcohol_level * 100

        # War betrunken (über 10%) und ist jetzt unter 10%?
        if self.was_drunk and current_alcohol_percent < 10:
            self.start_vomiting()
            self.was_drunk = False  # Reset flag

        # Setze Flag wenn Spieler betrunken wird (über 20%)
        if current_alcohol_percent > 20:
            self.was_drunk = True

    def apply_drunk_movement_chaos(self):
        """Wendet chaotische Bewegung bei Betrunkenheit an."""
        drunk_level = self.get_drunk_level()
        if drunk_level >= 1:  # Ab Level 1 beginnen leichte Effekte
            self.drunk_wobble_timer += 1
            self.random_movement_timer += 1

            # Zufällige spontane Bewegungen basierend auf Betrunkenheitsgrad
            if drunk_level >= 2:
                # Chance für zufällige Bewegung steigt mit Betrunkenheitsgrad
                random_chance = drunk_level * 0.008  # 0.8% bei Level 2, 2.4% bei Level 3, 3.2% bei Level 4

                if random.random() < random_chance:
                    # Zufällige Bewegungsrichtung für kurze Zeit
                    random_directions = [
                        (-1, 0),  # Links
                        (1, 0),   # Rechts
                        (0, -1),  # Oben
                        (0, 1),   # Unten
                        (-1, -1), # Links-Oben
                        (1, -1),  # Rechts-Oben
                        (-1, 1),  # Links-Unten
                        (1, 1),   # Rechts-Unten
                        (0, 0)    # Stoppen
                    ]

                    random_dir = random.choice(random_directions)

                    # Temporäre zufällige Bewegung (überschreibt Spielereingabe kurzzeitig)
                    if drunk_level >= 4:  # Bei sehr hoher Betrunkenheit stärkere Effekte
                        self.xdir = random_dir[0]
                        self.ydir = random_dir[1]
                    elif drunk_level >= 3:  # Bei hoher Betrunkenheit moderate Effekte
                        if random.random() < 0.7:  # 70% Chance die Richtung zu ändern
                            self.xdir = random_dir[0]
                            self.ydir = random_dir[1]
                    else:  # Bei mittlerer Betrunkenheit leichte Störungen
                        if random.random() < 0.4:  # 40% Chance für leichte Störung
                            # Nur kleine Abweichungen von der gewünschten Richtung
                            if self.xdir != 0 and random.random() < 0.3:
                                self.xdir *= -1  # Richtung umkehren
                            if self.ydir != 0 and random.random() < 0.3:
                                self.ydir *= -1  # Richtung umkehren

            # Kontinuierliches Torkeln (visuelle Effekte)
            if drunk_level >= 2:
                wobble_strength = drunk_level * 0.4
                wobble_x = math.sin(self.drunk_wobble_timer * 0.12) * wobble_strength
                wobble_y = math.cos(self.drunk_wobble_timer * 0.18) * wobble_strength

                # Anwenden der Torkelbewegung als kleine Verschiebung
                self.drunk_vision_offset_x = wobble_x
                self.drunk_vision_offset_y = wobble_y

            # Gelegentliches "Hängenbleiben" bei sehr hoher Betrunkenheit
            if drunk_level >= 4 and self.random_movement_timer % 120 == 0:  # Alle 2 Sekunden
                if random.random() < 0.15:  # 15% Chance
                    # Spieler bleibt kurz stehen (als ob er das Gleichgewicht verliert)
                    self.xdir = 0
                    self.ydir = 0

    def update_alcohol_system(self):
        """Aktualisiert das Alkohol-System jeden Frame."""
        # Nur wenn Alkohol aktiviert ist
        if not config.ALCOHOL_ENABLED:
            return

        # Alkohol-Abbau über Zeit
        if self.alcohol_level > 0:
            self.alcohol_level = max(0, self.alcohol_level - self.alcohol_decay_rate)

        # Prüfe ob Spieler ausnüchtert und kotzen muss
        self.check_sobering_up()

        # Aktualisiere Kotz-System
        self.update_vomiting()

        # Betrunkene Bewegungseffekte anwenden (nur wenn nicht am kotzen)
        if not self.is_vomiting:
            self.apply_drunk_movement_chaos()

        # Gelegentliche Hickser bei hohem Alkohol-Level
        import game_state
        if self.get_drunk_level() >= 3 and game_state.tick - self.last_hiccup_time > 180:  # Alle 3 Sekunden
            if random.random() < 0.1:  # 10% Chance
                # Hier könnte ein Hickser-Sound gespielt werden
                self.last_hiccup_time = game_state.tick

    def respawn(self):
        import game_state
        hit_player_index = game_state.gameScreen.players.index(self)

        if hit_player_index == 0:  # Player 1 hit
            self.xpos = config.PLAYER_1_STARTX * TILE_WIDTH
            self.ypos = config.PLAYER_1_STARTY * TILE_HEIGHT
        else:  # Player 2 hit
            self.xpos = config.PLAYER_2_STARTX * TILE_WIDTH
            self.ypos = config.PLAYER_2_STARTY * TILE_HEIGHT

        # Reset ammo for hit player
        self.ammo = config.INITIAL_AMMO
        self.dying = False
        self.sprite.speed = 6

        # Reset health to full
        self.health = self.max_health

        # Reset alcohol level for hit player (teilweise)
        self.alcohol_level = max(0, self.alcohol_level - 0.3)  # Schock nüchtert etwas auf

    def update(self):
        import game_state

        if self.dying:
            if self.sprite.lastPhase == 3:
                self.sprite.stop(False)
            if not game_state.message:
                self.respawn()
            return

        # Alkohol-System aktualisieren
        self.update_alcohol_system()

        new_xpos = self.xpos
        new_ypos = self.ypos

        new_xdir = self.xdir
        new_ydir = self.ydir

        # Geschwindigkeit basierend auf Alkohol-Level anpassen
        tempspeed = self.speed * self.get_drunk_speed_modifier()

        # collision with level border:
        if new_xpos < 0:
            new_xpos = 0
            new_xdir = 0

        if new_xpos > (game_state.level.getWidth() -1) * TILE_WIDTH:
            new_xpos = (game_state.level.getWidth() -1) * TILE_WIDTH
            new_xdir = 0

        if new_ypos < 0:
            new_ypos = 0
            new_ydir = 0

        if new_ypos > (game_state.level.getHeight() -1) * TILE_HEIGHT:
            new_ypos = (game_state.level.getHeight() -1) * TILE_HEIGHT
            new_ydir = 0

        # Duck Hunt mode: lock player to bottom Y position
        if getattr(config, 'DUCK_HUNT_MODE', False):
            duck_hunt_y = (game_state.level.getHeight() - 2) * TILE_HEIGHT  # Same as spawn position
            new_ypos = duck_hunt_y
            new_ydir = 0

        # collision with tiles:
        x1 = new_xpos // TILE_WIDTH
        y1 = new_ypos // TILE_HEIGHT
        x2 = (new_xpos + TILE_WIDTH -1) // TILE_WIDTH
        y2 = (new_ypos + TILE_HEIGHT -1) // TILE_HEIGHT

        # tiles for coll checK:
        #
        # t1 | t2
        # ---+---
        # t3 | t4

        t1 = game_state.level.getTile(x1, y1)
        t2 = game_state.level.getTile(x2, y1)
        t3 = game_state.level.getTile(x1, y2)
        t4 = game_state.level.getTile(x2, y2)

        t1blocked = t1 not in [' ', 'N']  # Allow movement through empty space and no-spawn zones
        t2blocked = t2 not in [' ', 'N']  # Allow movement through empty space and no-spawn zones
        t3blocked = t3 not in [' ', 'N']  # Allow movement through empty space and no-spawn zones
        t4blocked = t4 not in [' ', 'N']  # Allow movement through empty space and no-spawn zones

        if new_xdir < 0:   # going left
            if t1blocked and t3blocked:
                new_xdir = 0
            elif t1blocked and not t3blocked:
                new_xdir = 0
                new_ydir = 1
                tempspeed = 1
            elif not t1blocked and t3blocked:
                new_xdir = 0
                new_ydir = -1
                tempspeed = 1

        elif new_xdir > 0: # going right
            if t2blocked and t4blocked:
                new_xdir = 0
            elif t2blocked and not t4blocked:
                new_xdir = 0
                new_ydir = 1
                tempspeed = 1
            elif not t2blocked and t4blocked:
                new_xdir = 0
                new_ydir = -1
                tempspeed = 1

        elif new_ydir < 0: # going up
            if t1blocked and t2blocked:
                new_ydir = 0
            elif t1blocked and not t2blocked:
                new_ydir = 0
                new_xdir = 1
                tempspeed = 1
            elif not t1blocked and t2blocked:
                new_ydir = 0
                new_xdir = -1
                tempspeed = 1

        elif new_ydir > 0: # going down
            if t3blocked and t4blocked:
                new_ydir = 0
            elif t3blocked and not t4blocked:
                new_ydir = 0
                new_xdir = 1
                tempspeed = 1
            elif not t3blocked and t4blocked:
                new_ydir = 0
                new_xdir = -1
                tempspeed = 1

        # calculate new position
        new_xpos += new_xdir * tempspeed
        new_ypos += new_ydir * tempspeed

        # apply changed position
        self.xpos = new_xpos
        self.ypos = new_ypos

        # show animation and play footstep sound
        spriteAnim = self.facedir + (4 if self.showGun else 0)
        self.sprite.select(spriteAnim)

        if self.xdir == 0 and self.ydir == 0:
            self.sprite.stop()
        else:
            self.sprite.start()

            if game_state.tick % 8 == 0:
                playFootstepSound()

    def draw(self, output):
        """Überschreibt die Standard-Draw-Methode um Torkel- und Kotz-Effekte hinzuzufügen."""
        # Anwenden der Offsets für visuelle Effekte
        if self.is_vomiting:
            # Kotz-Effekt: stärkere Zittereffekte
            draw_x = self.xpos + self.drunk_vision_offset_x
            draw_y = self.ypos + self.drunk_vision_offset_y
        elif self.get_drunk_level() >= 2:
            # Torkel-Effekt bei Betrunkenheit
            draw_x = self.xpos + self.drunk_vision_offset_x
            draw_y = self.ypos + self.drunk_vision_offset_y
        else:
            draw_x = self.xpos
            draw_y = self.ypos

        # Apply drunk shader effects
        drunk_level = self.get_drunk_level()
        if drunk_level > 0 and config.ALCOHOL_ENABLED:
            self._draw_drunk_shader(output, draw_x, draw_y, drunk_level)
        else:
            self.sprite.draw(output, draw_x, draw_y)

        # Zeichne visuellen Kotz-Effekt
        if self.is_vomiting:
            from puke_effect import PukeEffect
            PukeEffect.draw_around_player(output, draw_x, draw_y, self.facedir)

    def _draw_drunk_shader(self, output, x, y, drunk_level):
        """Zeichnet den Spieler mit Betrunkenheits-Shader-Effekten."""

        # Erstelle eine temporäre Surface für Shader-Effekte
        sprite_surface = self._get_current_sprite_surface()
        if sprite_surface is None:
            return

        # Kopiere die Sprite-Surface für Manipulation
        drunk_surface = sprite_surface.copy()

        # Berechne Effekt-Intensität basierend auf Betrunkenheitsgrad
        intensity = drunk_level / 4.0  # Normalize to 0-1

        # 1. Color tinting effect (rotierende Farben bei Betrunkenheit)
        if drunk_level >= 1:
            tint_color = self._get_drunk_tint_color(drunk_level)
            # Erhöhe Intensität basierend auf Betrunkenheitsgrad
            tint_intensity = min(0.6, intensity * 0.4 + drunk_level * 0.1)
            self._apply_color_tint(drunk_surface, tint_color, tint_intensity)

        # 2. Transparency/Alpha effect (mehr transparent = betrunkener)
        if drunk_level >= 2:
            alpha = max(100, 255 - int(drunk_level * 30))  # Minimum 100 alpha
            drunk_surface.set_alpha(alpha)

        # 3. Delayed/Ghosting effect - zeichne vorherige Positionen
        if drunk_level >= 3:
            self._draw_ghost_trail(output, x, y, drunk_surface, intensity)

        # 4. Main sprite mit Distortion
        if drunk_level >= 4:
            # Starke Verzerrung bei sehr hoher Betrunkenheit
            drunk_surface = self._apply_distortion(drunk_surface, intensity)

        # Zeichne die finale manipulierte Surface
        output.blit(drunk_surface, (int(x), int(y)))

    def _get_current_sprite_surface(self):
        """Holt die aktuelle Sprite-Surface für Shader-Manipulation."""
        try:
            if hasattr(self.sprite, 'animations'):
                # AnimSprite
                if self.sprite.running:
                    phase = ((game_state.tick - self.sprite.startTime) // self.sprite.speed) % len(self.sprite.animations[0])
                else:
                    phase = self.sprite.lastPhase
                sprite = self.sprite.animations[self.sprite.anim][phase]
                return sprite.surface
            else:
                # Regular Sprite
                return self.sprite.surface
        except:
            return None

    def _get_drunk_tint_color(self, drunk_level):
        """Bestimmt die Farbtönung basierend auf Betrunkenheitsgrad mit 360° Rotation."""
        # Berechne Rotationsgeschwindigkeit basierend auf Betrunkenheitsgrad
        rotation_speed = drunk_level * 0.05  # Je betrunkener, desto schneller die Rotation

        # Berechne aktuellen Winkel basierend auf game_state.tick
        angle = (game_state.tick * rotation_speed) % (2 * math.pi)

        # Konvertiere Winkel zu RGB mit HSV-ähnlicher Berechnung
        # Erstelle einen vollen 360° Farbkreis
        def angle_to_rgb(angle_rad, saturation=1.0, value=1.0):
            """Konvertiert einen Winkel in Radiant zu RGB-Farbe."""
            # Normalisiere Winkel zu 0-1
            h = (angle_rad / (2 * math.pi)) % 1.0

            # HSV zu RGB Konversion (vereinfacht)
            if h < 1/6:  # Rot zu Gelb
                r, g, b = 1.0, h * 6, 0.0
            elif h < 2/6:  # Gelb zu Grün
                r, g, b = (2/6 - h) * 6, 1.0, 0.0
            elif h < 3/6:  # Grün zu Cyan
                r, g, b = 0.0, 1.0, (h - 2/6) * 6
            elif h < 4/6:  # Cyan zu Blau
                r, g, b = 0.0, (4/6 - h) * 6, 1.0
            elif h < 5/6:  # Blau zu Magenta
                r, g, b = (h - 4/6) * 6, 0.0, 1.0
            else:  # Magenta zu Rot
                r, g, b = 1.0, 0.0, (1.0 - h) * 6

            # Anpassung für Sättigung und Helligkeit
            r = int((r * saturation + (1 - saturation)) * value * 255)
            g = int((g * saturation + (1 - saturation)) * value * 255)
            b = int((b * saturation + (1 - saturation)) * value * 255)

            return (r, g, b)

        # Berechne Sättigung und Helligkeit basierend auf Betrunkenheitsgrad
        saturation = min(1.0, drunk_level * 0.3)  # Mehr Sättigung = betrunkener
        value = 0.8 + 0.2 * (drunk_level / 4.0)  # Leicht hellere Farben bei höherer Betrunkenheit

        return angle_to_rgb(angle, saturation, value)

    def _apply_color_tint(self, surface, tint_color, intensity):
        """Wendet eine Farbtönung auf die Surface an."""
        # Erstelle eine Tint-Surface mit der gewünschten Farbe
        tint_surface = pygame.Surface(surface.get_size(), flags=pygame.SRCALPHA)
        tint_surface.fill((*tint_color, int(255 * intensity)))

        # Wende die Tönung mit BLEND_MULT an
        surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)

    def _draw_ghost_trail(self, output, x, y, sprite_surface, intensity):
        """Zeichnet Ghost-Trail-Effekt für Betrunkenheit."""
        # Speichere aktuelle Position in History (vereinfacht)
        trail_positions = [
            (x - 2, y - 1),
            (x - 4, y - 1),
            (x - 6, y - 2)
        ]

        # Zeichne Ghost-Sprites mit abnehmender Transparenz
        for i, (ghost_x, ghost_y) in enumerate(trail_positions):
            ghost_alpha = max(30, int(100 * intensity * (0.7 ** i)))
            ghost_surface = sprite_surface.copy()
            ghost_surface.set_alpha(ghost_alpha)

            # Verwende die rotierende Farbe auch für Ghosts, aber mit Offset
            angle_offset = i * math.pi / 3  # Jeder Ghost hat einen anderen Farbwinkel
            rotation_speed = 0.08
            angle = ((game_state.tick - i * 5) * rotation_speed + angle_offset) % (2 * math.pi)

            # Berechne Ghost-Farbe basierend auf rotierendem Winkel
            h = (angle / (2 * math.pi)) % 1.0
            if h < 1/3:
                ghost_color = (int(255 * (1 - h * 3)), 255, int(255 * h * 3))
            elif h < 2/3:
                ghost_color = (0, int(255 * (2 - h * 3)), 255)
            else:
                ghost_color = (int(255 * (h * 3 - 2)), 0, int(255 * (3 - h * 3)))

            # Wende Ghost-Farbtönung an
            ghost_tint = pygame.Surface(ghost_surface.get_size(), flags=pygame.SRCALPHA)
            ghost_tint.fill((*ghost_color, ghost_alpha // 3))
            ghost_surface.blit(ghost_tint, (0, 0), special_flags=pygame.BLEND_MULT)

            output.blit(ghost_surface, (int(ghost_x), int(ghost_y)))

    def _apply_distortion(self, surface, intensity):
        """Wendet Verzerrungseffekte auf die Surface an."""
        try:
            # Erstelle leichte Wellenbewegung
            import math
            width, height = surface.get_size()
            distorted = pygame.Surface((width, height), flags=pygame.SRCALPHA)

            wave_amplitude = int(2 * intensity)
            wave_frequency = 0.3

            for y in range(height):
                wave_offset = int(wave_amplitude * math.sin(y * wave_frequency + game_state.tick * 0.1))
                for x in range(width):
                    src_x = x - wave_offset
                    if 0 <= src_x < width:
                        try:
                            pixel = surface.get_at((src_x, y))
                            distorted.set_at((x, y), pixel)
                        except:
                            pass

            return distorted
        except:
            # Fallback wenn Distortion fehlschlägt
            return surface


