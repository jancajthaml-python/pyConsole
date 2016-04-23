# import itertools

from ..utils import call

from .split import SplitScreen


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

    def render(self, canvas, x, y):
        self.a.render(canvas, self.x, self.y)
        self.b.render(canvas, self.x + self.left_half, self.y)
