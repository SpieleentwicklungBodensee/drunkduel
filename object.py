# Override print function
import ledwall
print = ledwall.print


class Object:
    def __init__(self, xpos, ypos, sprite):
        self.xpos = xpos
        self.ypos = ypos
        self.sprite = sprite

    def draw(self, output):
        self.sprite.draw(output, self.xpos, self.ypos)