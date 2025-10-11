#########################
###
### BitmapFont
### by zeha@drwuro.com
###
### version 1.3 (2025)
###
#########################

"""
BitmapFont - A retro-style bitmap font renderer for pygame

This module provides a bitmap font system that loads a character sheet image
and renders text using individual character sprites. It supports colored text,
background colors, text caching for performance, and positioning utilities.

The font expects a character sheet with 96 ASCII characters (from space to DEL)
arranged horizontally in a single row.
"""

import pygame

# Number of characters in the bitmap font (ASCII 32-127: space to DEL)
NUM_CHARS = 96
# Enable text caching to improve performance for repeated text rendering
TEXT_CACHING = True

class BitmapFont:
    """
    A bitmap font renderer that uses a character sheet image to display text.
    
    This class loads a bitmap font from an image file where characters are
    arranged horizontally in a single row. It provides methods for rendering
    text with custom colors, positioning, and caching for performance.
    """
    
    def __init__(self, filename, char_w=8, char_h=8, zoom=1, scr_w=320, scr_h=240):
        """
        Initialize the bitmap font renderer.
        
        Args:
            filename (str): Path to the bitmap font image file
            char_w (int): Width of each character in pixels (default: 8)
            char_h (int): Height of each character in pixels (default: 8)
            zoom (int): Scale factor for the font (default: 1)
            scr_w (int): Screen width for centering calculations (default: 320)
            scr_h (int): Screen height for positioning (default: 240)
        """
        # Track the last text position for sequential text output
        self.lastxpos, self.lastypos = 0, 0

        # Store original character dimensions
        self.char_w = char_w
        self.char_h = char_h

        # Screen dimensions for text positioning calculations
        self.scr_w = scr_w
        self.scr_h = scr_h

        # Dictionary to store colored versions of the font
        self.fonts = {}

        # Remember the last used color
        self.lastcolor = (255, 255, 255)

        # Load the bitmap font image
        self.font = pygame.image.load(filename)

        # Apply zoom scaling to character dimensions
        self.char_w *= zoom
        self.char_h *= zoom

        # Cache for rendered text surfaces to improve performance
        self.textCache = {}

    def initColor(self, c):
        """
        Create a colored version of the font and cache it.
        
        This method scales the font image and applies a color multiplication
        to create a colored version of the font for faster rendering.
        
        Args:
            c (tuple): RGB color tuple (r, g, b) for the font color
        """
        # Scale the font to the correct size and apply color
        f = pygame.transform.scale(self.font, (self.char_w * NUM_CHARS, self.char_h))
        f.fill(c, special_flags=pygame.BLEND_MULT)
        self.fonts[c] = f

    def drawText(self, output, text, x=None, y=None, fgcolor=None, bgcolor=None):
        """
        Draw text on the output surface at the specified position.
        
        This is the main text rendering method. It supports colored text,
        background colors, and uses caching for improved performance when
        rendering the same text multiple times.
        
        Args:
            output (pygame.Surface): The surface to draw text on
            text (str): The text string to render
            x (int, optional): X position in character units (uses last position if None)
            y (int, optional): Y position in character units (uses last position if None)
            fgcolor (tuple, optional): RGB foreground color (uses last color if None)
            bgcolor (tuple, optional): RGB background color (transparent if None)
        """
        # Use last position if coordinates not specified
        if x is None:
            x = self.lastxpos
        if y is None:
            y = self.lastypos

        # Use last color if foreground color not specified
        if fgcolor is None:
            fgcolor = self.lastcolor
        else:
            self.lastcolor = fgcolor

        # Draw background rectangle if background color specified
        if bgcolor is not None:
            output.fill(bgcolor, (x * self.char_w,
                                 (y * self.char_h),
                                 len(text) * self.char_w,
                                 (self.char_h))
                                 )

        # Initialize color version of font if not already cached
        if fgcolor not in self.fonts:
            self.initColor(fgcolor)

        # Use text caching for better performance
        if TEXT_CACHING:
            # Create cache key from text and colors
            key = (text, fgcolor, bgcolor)

            # Create cached surface if not already cached
            if key not in self.textCache:
                cacheSurface = pygame.Surface((len(text) * self.char_w, self.char_h), flags=pygame.SRCALPHA)

                # Render each character to the cache surface
                for i, c in enumerate(text):
                    # Calculate source position in font sheet (ASCII offset)
                    grabx = (ord(c) - 32) * self.char_w
                    blitx = i * self.char_w
                    blity = (self.char_h - self.char_h + 1) / 2

                    cacheSurface.blit(self.fonts[fgcolor], (blitx, blity), (grabx, 0, self.char_w, self.char_h))
                    self.textCache[key] = cacheSurface
            else:
                # Use existing cached surface
                cacheSurface = self.textCache[key]

            # Blit the cached text surface to output
            blitx = x * self.char_w
            blity = y * self.char_h + (self.char_h - self.char_h + 1) / 2
            output.blit(cacheSurface, (blitx, blity))
        else:
            # Render without caching (character by character)
            for i, c in enumerate(text):
                # Calculate source and destination positions
                grabx = (ord(c) - 32) * self.char_w
                blitx = (x + i) * self.char_w
                blity = y * self.char_h + (self.char_h - self.char_h + 1) / 2

                output.blit(self.fonts[fgcolor], (blitx, blity), (grabx, 0, self.char_w, self.char_h))

        # Update cursor position for next text output
        self.lastxpos = x
        self.lastypos = y + 1

    def centerText(self, output, text, y=None, fgcolor=None, bgcolor=None, align=True):
        """
        Draw text centered horizontally on the screen.
        
        This method calculates the horizontal center position based on the
        screen width and text length, then draws the text at that position.
        
        Args:
            output (pygame.Surface): The surface to draw text on
            text (str): The text string to render
            y (int, optional): Y position in character units (uses last position if None)
            fgcolor (tuple, optional): RGB foreground color (uses last color if None)
            bgcolor (tuple, optional): RGB background color (transparent if None)
            align (bool): Whether to use integer alignment (default: True)
        """
        # Calculate centered X position
        if align:
            # Integer-aligned centering
            x = ((self.scr_w // self.char_w) - len(text) +1) // 2
        else:
            # Floating-point centering
            x = ((self.scr_w // self.char_w) - len(text)) / 2

        # Draw the text at the calculated center position
        self.drawText(output, text, x, y, fgcolor, bgcolor)

    def locate(self, x=None, y=None):
        """
        Set the cursor position for subsequent text output.
        
        This method allows you to position the cursor at specific coordinates
        in character units. Subsequent calls to drawText() without explicit
        coordinates will use this position.
        
        Args:
            x (int, optional): X position in character units (unchanged if None)
            y (int, optional): Y position in character units (unchanged if None)
        """
        if x is not None:
            self.lastxpos = x
        if y is not None:
            self.lastypos = y

    def locateRel(self, x=None, y=None):
        """
        Move the cursor position relative to the current position.
        
        This method allows you to move the cursor by a relative offset
        from its current position in character units.
        
        Args:
            x (int, optional): X offset in character units (no change if None)
            y (int, optional): Y offset in character units (no change if None)
        """
        if x is not None:
            self.lastxpos += x
        if y is not None:
            self.lastypos += y

