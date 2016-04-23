# fixme problem with focus capture


class VoidScreen(object):

    def __init__(self, *args):
        self.width = 0
        self.height = 0

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h

    def render(self, canvas):
        return [(' ' * self.width)] * (self.height)
