class VerticalScrollableScreen(object):

    def __init__(self, data):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        # fixme change to setData and preparse in that method
        self.data = data
        self.selected = None
        self.yOffset = 0
        self.focus = False

        # fixme add pointer to selected item

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self.data

    def __del__(self):
        del self.data

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
        pass

    def onBlur(self):
        self.focus = False
        return True

    def onFocus(self):
        self.focus = True
        return True

    def hasFocus(self):
        return self.focus

    def render(self, canvas, x, y):
        w = self.width
        h = self.height
        self.selected = None
        start = max(0, min(len(self.data) - h, len(self.data) - (h / 2) - self.yOffset))  # noqa
        end = min(len(self.data), start + h)

        cursor = (len(self.data) - self.yOffset - 1) - start

        total_lines = 0

        i = start

        fill = ' ' * w

        def draw_selected_focus(line):
            return '\033[0;37;41m{0}\033[0m'.format(line[:w] + fill[:-len(line)])  # noqa

        def draw_selected_blur(line):
            return '\033[0;37;40m{0}\033[0m'.format(line[:w] + fill[:-len(line)])  # noqa

        def draw_unselected(line):
            return line[:w] + fill[:-len(line)]

        def draw_line(line):
            if total_lines < h:
                if total_lines == cursor:
                    if self.focus:
                        self.selected = line['id']
                        line = draw_selected_focus(' ' + line['label'] + ' ')
                    else:
                        line = draw_selected_blur(' ' + line['label'] + ' ')
                else:
                    line = draw_unselected(' ' + line['label'] + ' ')

                canvas.append('\033[{1};{0}H{2}'.format(x, y + total_lines, line))  # noqa
                return True
            else:
                return False

        while True:
            if i >= end or not draw_line(self.data[i]):
                break

            total_lines += 1
            i += 1
