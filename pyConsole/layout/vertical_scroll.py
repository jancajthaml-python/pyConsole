from ..utils import publish


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
                    if not draw_line(line[j:j + w]):
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

        # fixme now I have processed lines need to loop throught them again and
        # set selected row

        return view
