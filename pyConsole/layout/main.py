import sys

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

        self.content.onResize(x + 2, y + 1, w - 2, h - 2)

        self.clear = ''.join([
            '\033[{0};0H\033[0m \033[{0};{1}H\033[0m '.format(i, self.width) for i in xrange(1, self.height + 2)  # noqa
        ]) + '\033[1;2H\033[0m{1}\033[{0};2H\033[0m{1}'.format(self.height, ' ' * (self.width - 1))  # noqa

        # fixme change to publish repaint
        self.render()

    def onKeyDown(self, key):
        # fixme change to publish repaint
        if self.content.onKeyDown(key):
            self.render()

    def render(self):
        sys.stdout.write(''.join(self.content.render()) + self.clear)
