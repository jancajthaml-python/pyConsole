#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import os
import fcntl
import termios
import struct

from .utils import publish
from layout import MainScreen


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


def init():
    MainScreen()


def resize(*args):
    h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))  # noqa
    publish('resize', 0, 0, w, h)


def start():

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
                            publish('key_down', a + b + c)
                        else:
                            break
                        continue
                    else:
                        publish('key_down', a)
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
