
"""
Player class and related functionality for Drunk Duel.
Handles player movement, collision detection, and interactions.
"""
import controls
import random
import math
from object import Object
from sprite import createAnimatedSprite
from game_logic import spawnBullet
from sound_manager import playFootstepSound, SFX_GUNSHOT

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

    def moveLeft(self):
        self.xdir = -1
        self.ydir = 0
        self.facedir = controls.DIR_LEFT

    def moveRight(self):
        self.xdir = 1
        self.ydir = 0
        self.facedir = controls.DIR_RIGHT

    def moveUp(self):
        self.xdir = 0
        self.ydir = -1
        self.facedir = controls.DIR_UP

    def moveDown(self):
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

    def shoot(self, player_index):
        if self.ammo <= 0:
            return  # Can't shoot without ammo

        self.showGun = True
        self.ammo -= 1

        # Alkohol beeinflusst die Schussrichtung
        accuracy_modifier = self.get_drunk_accuracy_modifier()
        
        if self.xpos < 128:
            bulletxdir = 1
            self.facedir = controls.DIR_RIGHT
        else:
            bulletxdir = -1
            self.facedir = controls.DIR_LEFT
            
        # Bei Betrunkenheit: zufällige Abweichung der Schussrichtung
        if accuracy_modifier < 1.0:
            if random.random() > accuracy_modifier:
                # Schuss geht in zufällige Richtung
                directions = [-1, 1]
                bulletxdir = random.choice(directions)

        # Get bullet sprite from game state
        import game_state
        if hasattr(game_state, 'bullet_sprite'):
            bullet_sprite = game_state.bullet_sprite
        else:
            # Fallback: load directly
            from sprite import Sprite
            bullet_sprite = Sprite('gfx/bullet.png')
        
        spawnBullet(self.xpos, self.ypos, bulletxdir, player_index, bullet_sprite)
        SFX_GUNSHOT.play(loops=0)

    def stopShooting(self):
        self.showGun = False

    def drink_alcohol(self, amount=0.3):
        """Spieler trinkt Alkohol und wird betrunkener."""
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
        # Alkohol-Abbau über Zeit
        if self.alcohol_level > 0:
            self.alcohol_level = max(0, self.alcohol_level - self.alcohol_decay_rate)
            
        # Betrunkene Bewegungseffekte anwenden
        self.apply_drunk_movement_chaos()
        
        # Gelegentliche Hickser bei hohem Alkohol-Level
        import game_state
        if self.get_drunk_level() >= 3 and game_state.tick - self.last_hiccup_time > 180:  # Alle 3 Sekunden
            if random.random() < 0.1:  # 10% Chance
                # Hier könnte ein Hickser-Sound gespielt werden
                self.last_hiccup_time = game_state.tick

    def update(self):
        import game_state
        from game_state import TILE_WIDTH, TILE_HEIGHT
        
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

        t1blocked = t1 != ' '
        t2blocked = t2 != ' '
        t3blocked = t3 != ' '
        t4blocked = t4 != ' '

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
        """Überschreibt die Standard-Draw-Methode um Torkel-Effekte hinzuzufügen."""
        # Anwenden der Torkel-Offsets für visuellen Effekt
        drunk_level = self.get_drunk_level()
        if drunk_level >= 2:
            draw_x = self.xpos + self.drunk_vision_offset_x
            draw_y = self.ypos + self.drunk_vision_offset_y
        else:
            draw_x = self.xpos
            draw_y = self.ypos
            
        self.sprite.draw(output, draw_x, draw_y)


