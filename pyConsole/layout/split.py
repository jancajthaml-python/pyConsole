from ..utils import call
from ..utils import publish


class SplitScreen(object):

    def __init__(self, **kwargs):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.a = kwargs.get('left', None) or kwargs.get('top', None)
        self.b = kwargs.get('right', None) or kwargs.get('bottom', None)

    def hasFocus(self):
        return call(self.a, 'hasFocus') or\
            call(self.b, 'hasFocus')

    def onBlur(self):
        return call(self.a, 'onBlur') and\
            call(self.b, 'onBlur')

    def onFocus(self):
        if call(self.a, 'onFocus'):
            return call(self.b, 'onBlur')
        elif call(self.b, 'onFocus'):
            return call(self.a, 'onBlur')

    def onScroll(self, direction):
        call(self.a, 'onScroll', direction)
        call(self.b, 'onScroll', direction)

    def captureFocus(self, direction=1):
        a = self.a if direction == 1 else self.b
        b = self.b if direction == 1 else self.a

        if call(a, 'hasFocus'):
            if isinstance(a, SplitScreen):
                if a.captureFocus(direction):
                    return True
            call(a, 'onBlur')
            if isinstance(b, SplitScreen):
                return b.captureFocus(direction)
            elif call(b, 'onFocus'):
                return True
        elif call(b, 'hasFocus'):
            if isinstance(b, SplitScreen):
                if b.captureFocus(direction):
                    return True
        else:
            if isinstance(a, SplitScreen):
                if a.captureFocus(direction):
                    return True
            if call(a, 'onFocus'):
                return True

        return False

    def onKeyDown(self, key):
        if key == '\t':
            publish('event', 'focus_cycle_forward')
            if self.captureFocus(1):
                return True
            else:
                self.onFocus()
                return True
        elif key == '\x1b[A':
            self.onScroll(1)
            publish('event', 'key[up]')
        elif key == '\x1b[B':
            self.onScroll(-1)
            publish('event', 'key[down]')
        elif key == '\x1b[C':
            publish('event', 'focus_next')
            # fixme dont use return code use publishing repaint
            return self.captureFocus(1)
        elif key == '\x1b[D':
            publish('event', 'focus_prev')
            # fixme dont use return code use publishing repaint
            return self.captureFocus(-1)
        else:
            call(self.a, 'onKeyDown', key)
            call(self.b, 'onKeyDown', key)
