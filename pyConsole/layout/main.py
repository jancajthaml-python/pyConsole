import sys
from ..utils import subscribe
from ..utils import unsubscribe


class MainScreen(object):

    def __init__(self):
        self.content = None
        subscribe('set_screen', self.setScreen)
        subscribe('repaint', self.render)
        subscribe('resize', self.onResize)
        subscribe('key_down', self.onKeyDown)

    def __enter__(self):
        return self

    def __del__(self):
        unsubscribe('set_screen', self.setScreen)
        unsubscribe('repaint', self.render)
        unsubscribe('resize', self.onResize)
        unsubscribe('key_down', self.onKeyDown)
        del self.content

    def __exit__(self, type, value, traceback):
        unsubscribe('set_screen', self.setScreen)
        unsubscribe('repaint', self.render)
        unsubscribe('resize', self.onResize)
        unsubscribe('key_down', self.onKeyDown)
        del self.content

    def setScreen(self, content):
        self.content = content
        self.content.onFocus()

    def onScroll(self, direction):
        if self.content:
            self.content.onScroll(direction)
            self.render()

    def onResize(self, x, y, w, h):
        if self.content:
            self.content.onResize(x + 2, y + 2, w - 2, h - 2)

        sys.stdout.write('\033[H\033[J\033[H')

        if self.content:
            self.render()

    def onKeyDown(self, key):
        if self.content:
            # fixme change to publish repaint
            if self.content.onKeyDown(key):
                self.render()

    def render(self):
        self.buffer = []
        if self.content:
            self.content.render(self.buffer, 0, 0)
        sys.stdout.write(''.join(self.buffer))  # noqa
