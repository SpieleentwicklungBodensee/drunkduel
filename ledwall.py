import pygame
import time
from bitmapfont import BitmapFont


SCR_W = 256
SCR_H = 320

window = None   # the actual ui window
output = None   # the render target
scaled = None   # scale surface to distort output
overlay = None  # vertical masking stripes

brightnessValue = -4
showOverlay = True

renderMode = 'led'

pygame.display.init()

fonts = {}
fontFilename = 'gfx/wurofont.png'
fontCharsize = (8, 8)
lastFontColor = (255, 255, 255)
lastPrintTime = 0

printMessages = []

_originalPrintFunction = print

def initFont(filename, char_w=8, char_h=8, zoom=1):
    fonts[zoom] = BitmapFont(filename, scr_w=SCR_W, scr_h=SCR_H, char_w=char_w, char_h=char_h, zoom=zoom)

for i in range(1, 3):
    initFont(fontFilename, fontCharsize[0], fontCharsize[1], zoom=i)


# -- screen handling and composing

def initScreen(mode='led'):
    global window, output, scaled, overlay, renderMode

    renderMode = mode

    if renderMode == 'led':
        window = pygame.display.set_mode((1920, 1080), flags=pygame.FULLSCREEN)
        output = pygame.Surface((SCR_W, SCR_H))
        scaled = pygame.Surface((SCR_W * 2, SCR_H))
        overlay = pygame.Surface((SCR_W * 2, SCR_H), flags=pygame.SRCALPHA)

        for x in range(SCR_W):
            pygame.draw.line(overlay, (0, 0, 0), (x * 2, 0), (x * 2, SCR_H))

    elif renderMode == 'plain':
        window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)
        output = window

    return output

def compose(do_cls=False):
    _drawPrintLog()
    if do_cls:
        cls()

    if renderMode == 'plain':
        pass

    elif renderMode == 'led':
        pygame.transform.scale(output, (SCR_W * 2, SCR_H), scaled)
        window.blit(scaled, (0, 0))
        if showOverlay:
            window.blit(overlay, (0, 0))

    pygame.display.flip()

def enableOverlay(flag=True):
    global showOverlay
    showOverlay = flag

def setBrightnessValue(b):
    global brightnessValue
    brightnessValue = b


# -- color conversion

def gamma(v):
    return min(v * 2**(brightnessValue / 4), 255)

def brightness(color):
    color = list(color)
    if isinstance(color[0], (list, tuple)):
        result = []
        for co in color:
            result.append(tuple([gamma(c) for c in co]))
        return result
    return tuple([gamma(c) for c in color])


# -- text drawing using the bitmapfont

def drawText(text, x=None, y=None, color=None, fontsize=1, center=False, align=True):
    global lastFontColor

    if not fontsize in fonts:
        initFont(fontFilename, fontCharsize[0], fontCharsize[1], fontsize)

    font = fonts[fontsize]

    if color is None:
        color = lastFontColor
    lastFontColor = color

    color = brightness(color)

    if center:
        font.centerText(output, text, y=y, fgcolor=color, align=align)
    else:
        font.drawText(output, text, x=x, y=y, fgcolor=color)

def centerText(text, y=None, color=None, fontsize=1, align=True):
    drawText(text, y=y, color=color, fontsize=fontsize, center=True, align=align)

def print(*args):
    text = ' '.join([str(arg) for arg in args])
    lines = text.split('\n')

    charsPerLine = SCR_W // fonts[1].char_w

    for line in lines:
        if not line:
            printMessages.append('')
            continue
        while len(line) > 0:
            printMessages.append(line[:charsPerLine])
            line = line[charsPerLine:]

    global lastPrintTime
    lastPrintTime = time.time()

    _originalPrintFunction(*args)

def cls():
    printMessages.clear()

def _drawPrintLog():
    global lastFontColor

    font = fonts[1]
    maxlines = SCR_H // font.char_h

    font.locate(0, 0)

    colorBackup = lastFontColor

    for line in printMessages[-maxlines:]:
        drawText(line.upper(), color=(192, 192, 192))

    lastFontColor = colorBackup

    if time.time() - lastPrintTime > 3:
        cls()
