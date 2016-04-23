import sys
# import itertools
# import numpy

from ..utils import subscribe


class MainScreen(object):

    def __init__(self, content):
        self.width = 0
        self.height = 0
        self.content = content
        self.clear = ''
        self.content.onFocus()
        subscribe('repaint', self.render)

    def onScroll(self, direction):
        self.content.onScroll(direction)
        self.render()

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h

        self.content.onResize(x + 2, y + 2, w - 2, h - 2)

        sys.stdout.write('\033[H\033[J\033[H')
        # self.clear = '\033[H\033[J\033[H'
        self.render()

    def onKeyDown(self, key):
        # fixme change to publish repaint
        if self.content.onKeyDown(key):
            self.render()

    def render(self):
        self.buffer = []
        self.content.render(self.buffer, 0, 0)
        sys.stdout.write(''.join(self.buffer))  # noqa
