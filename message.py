import ledwall

import game_state
from object import Object

class Message(Object):
    def __init__(self, xpos, ypos, lines, color):
        super().__init__(xpos, ypos, None)
        self.lines = lines
        self.color = color

        self.initTime = game_state.tick
        print(game_state.tick)

    def draw(self, output):
        for i, line in enumerate(self.lines):
            if (i -1) < (game_state.tick - self.initTime) // 32:
                ledwall.drawText(line.upper(), self.xpos, self.ypos + i, self.color)

    def isDue(self):
        if (game_state.tick - self.initTime) // 32 > len(self.lines) + 2:
            return True

        return False
