import ledwall

import game_state
import sound_manager
import config
from object import Object

# Override print function
import ledwall
print = ledwall.print


WORD_DURATION = 35


class Message(Object):
    def __init__(self, xpos, ypos, lines, color):
        super().__init__(xpos, ypos, None)
        self.lines = lines
        self.color = color

        self.initTime = game_state.tick

    def draw(self, output):
        for i, line in enumerate(self.lines):
            if (i -1) < (game_state.tick - self.initTime) // WORD_DURATION:
                ledwall.drawText(line.upper(), self.xpos, self.ypos + i, self.color)


    def update(self):
        if (game_state.tick - self.initTime) % WORD_DURATION != 0:
            return

        lineno = (game_state.tick - self.initTime) // WORD_DURATION

        if lineno >= len(self.lines):
            return

        line = self.lines[lineno]

        if line in sound_manager.SOUND_WORDS:
            sound = sound_manager.SOUND_WORDS[line]

            if type(sound) is tuple:
                if config.ACCURATE_INTONATION and lineno == len(self.lines) -1:
                    sound[1].play()
                else:
                    sound[0].play()
            else:
                sound.play()


    def isDue(self):
        if (game_state.tick - self.initTime) // 32 > len(self.lines) + 1:
            return True

        return False
