#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import os
import fcntl
import termios
import struct
import itertools

subscriptions = {}


def subscribe(message, subscriber):
    if message not in subscriptions:
        subscriptions[message] = [subscriber]
    else:
        subscriptions[message].append(subscriber)


def publish(message, *args, **kwargs):
    if message in subscriptions:
        for subscriber in subscriptions[message]:
            try:
                subscriber(*args, **kwargs)
            except Exception:
                pass


def call(obj, method, *args):
    if method in dir(obj):
        try:
            return getattr(obj, method)(*args)
        except AttributeError:
            return False
    else:
        return False


class ExitException(Exception):
    pass


def exit(signum, frame):
    raise ExitException, "ESC key detected"

signal.signal(signal.SIGALRM, exit)

block = os.O_NONBLOCK if 'O_NONBLOCK' in dir(os) else (
    os.NOBLOCK if 'NONBLOCK' in dir(os) else None)

r = sys.stdin.fileno()
w = sys.stdout.fileno()

r_flags = fcntl.fcntl(r, fcntl.F_GETFL)

if r_flags & block:
    fcntl.fcntl(r, fcntl.F_SETFL, r_flags & ~block)

w_flags = fcntl.fcntl(w, fcntl.F_GETFL)
if w_flags & block:
    fcntl.fcntl(w, fcntl.F_SETFL, w_flags | block)

# fixme problem with focus capture


class VoidScreen(object):

    def __init__(self, *args):
        self.width = 0
        self.height = 0

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h

    def render(self):
        return [(' ' * self.width)] * (self.height)


class VerticalScrollableScreen(object):

    def __init__(self, data):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        # fixme change to setData and preparse in that method
        self.data = data

        self.yOffset = 0
        self.focus = False

        # fixme add pointer to selected item

    def onScroll(self, direction):
        if self.focus:
            # fixme data can become multiline
            newY = min(len(self.data) - 1, max(0, self.yOffset + direction))  # noqa
            if newY != self.yOffset:
                self.yOffset = newY

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h
        self.x = x
        self.y = y

    def onKeyDown(self, key):
        if self.focus:
            publish('event', 'key[{0}]'.format(repr(key)))

    def onBlur(self):
        self.focus = False
        return True

    def onFocus(self):
        self.focus = True
        return True

    def hasFocus(self):
        return self.focus

    def render(self):
        w = self.width
        h = self.height

        # def preprocess_data(data):

        # data = preprocess_data(self.data)

        start = max(0, min(len(self.data) - h, len(self.data) - (h / 2) - self.yOffset))  # noqa
        end = min(len(self.data), start + h)

        cursor = (len(self.data) - self.yOffset - 1) - start

        view = []
        pointer = 0
        total_lines = 0

        i = start

        # firstly chunk lines by width

        # then recalculate start and end if neccessary

        # then iterate them

        def draw_line(line):
            if not len(line):
                line = (' ' * w)
            elif len(line) < w:
                line = line + (' ' * w)[:-len(line)]

            # remove does not work for multiline string
            if total_lines < h:
                if pointer == cursor:
                    if self.focus:
                        view.append('\033[41m\033[37m{0}\033[0m'.format(line))  # noqa
                    else:
                        view.append('\033[40m\033[37m{0}\033[0m'.format(line))  # noqa
                else:
                    view.append(line)
                return True
            else:
                return False

        while True:
            if i >= end:
                break

            line = self.data[i]

            if len(line) < w:
                if not draw_line(line + (' ' * w)[:-len(line)]):
                    break
                total_lines += 1
                pointer += 1
            elif len(line) > w:
                for j in range(0, len(line), w):
                    if not draw_line(line[j:j+w]):
                        break
                    total_lines += 1
                pointer += 1
            elif len(line):
                if not draw_line(line):
                    break
                total_lines += 1
                pointer += 1

            i += 1

        # remove does not work for multiline string
        if h > pointer:
            view.extend([(' ' * w) + '\033[0m'] * (h - pointer))

        #fixme now I have processed lines need to loop throught them again and
        #set selected row

        return view


class SplitScreen(object):

    def __init__(self, **kwargs):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.a = kwargs.get('left', None) or kwargs.get('top', None) or VoidScreen()  # noqa
        self.b = kwargs.get('right', None) or kwargs.get('bottom', None) or VoidScreen()  # noqa

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


class VerticalSplitScreen(SplitScreen):

    def __init__(self, **kwargs):
        super(VerticalSplitScreen, self).__init__(**kwargs)
        self.top_height = self.a.height if self.a.height > 0 else None
        self.bottom_height = self.b.height if self.b.height > 0 else None

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h
        self.x = x
        self.y = y

        if self.top_height and self.bottom_height:
            top_half = self.top_height
            bottom_half = self.bottom_height
        elif self.top_height:
            if self.top_height < h:
                top_half = self.top_height
            else:
                top_half = h + 1
            bottom_half = h - top_half
        elif self.bottom_height:
            bottom_half = self.bottom_height
            top_half = h - bottom_half
        else:
            top_half = int(round(h / 2, 0))
            bottom_half = h - top_half

        self.top_half = top_half
        self.bottom_half = bottom_half

        self.a.onResize(x, y, w, self.top_half)
        self.b.onResize(x, y + self.top_half, w, self.bottom_half)

    def render(self):
        out = []

        index = self.y

        a = call(self.a, 'render') or []
        b = call(self.b, 'render') or []

        for item in a:
            index += 1
            out.append(u'\033[{1};{0}H{2}'.format(self.x, index, item))  # noqa

        index = self.y

        for item in b:
            index += 1
            out.append(u'\033[{1};{0}H{2}'.format(self.x, index + self.top_half, item))  # noqa

        return out


class HorizontalSplitScreen(SplitScreen):

    def __init__(self, **kwargs):
        super(HorizontalSplitScreen, self).__init__(**kwargs)
        self.left_width = self.a.width if self.a.width > 0 else None
        self.right_width = self.b.width if self.b.width > 0 else None

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h
        self.x = x
        self.y = y

        left_half = None
        right_half = None

        if self.left_width and self.right_width:
            left_half = self.left_width
            right_half = self.right_width
        elif self.left_width:
            left_half = self.left_width
            right_half = w - left_half
        elif self.right_width:
            right_half = self.right_width
            left_half = w - right_half
        else:
            left_half = int(round(w / 2, 0))
            right_half = w - left_half

        self.left_half = left_half
        self.right_half = right_half

        call(self.a, 'onResize', x, y, self.left_half, h)
        call(self.b, 'onResize', x + self.left_half, y, self.right_half, h)

    def render(self):
        out = []

        index = self.y

        a = self.a.render()
        b = self.b.render()

        for left, right in itertools.izip_longest(a, b):
            index += 1
            if left:
                out.append(u'\033[{1};{0}H{2}'.format(self.x, index, left))  # noqa
            if right:
                out.append(u'\033[{1};{0}H{2}'.format(self.x + self.left_half, index, right))  # noqa

        return out


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


def start(screen):
    mainScreen = MainScreen(screen)

    def resize(*args):
        h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))  # noqa
        mainScreen.onResize(0, 0, w, h)

    # fixme publish event
    signal.signal(signal.SIGWINCH, resize)

    try:
        sys.stdout.write('\033[?1049h\033[?25l')
        resize()
        r_old = termios.tcgetattr(r)
        r_new = termios.tcgetattr(r)
        r_new[3] = r_new[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(r, termios.TCSANOW, r_new)

        try:
            while 1:
                try:
                    a = sys.stdin.read(1)
                    if a == chr(27):
                        signal.setitimer(signal.ITIMER_REAL, 0.01, 0.01)
                        b = sys.stdin.read(1)
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        if b == '[':
                            c = sys.stdin.read(1)
                            mainScreen.onKeyDown(a + b + c)
                        else:
                            break
                        continue
                    else:
                        mainScreen.onKeyDown(a)
                except IOError:
                    pass
                except ExitException:
                    break
        finally:
            termios.tcsetattr(r, termios.TCSAFLUSH, r_old)
    except KeyboardInterrupt:
        pass
    finally:
        fcntl.fcntl(r, fcntl.F_SETFL, r_flags)
        fcntl.fcntl(w, fcntl.F_SETFL, w_flags)
        sys.stdout.write('\033[?1049l\033[?25h')
