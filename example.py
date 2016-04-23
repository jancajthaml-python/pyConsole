
from pyConsole import VerticalSplitScreen
from pyConsole import HorizontalSplitScreen
from pyConsole import VerticalScrollableScreen
from pyConsole import start
from pyConsole import publish
from pyConsole import subscribe


class Header(object):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.title = 'static header'

    def onScroll(self, direction):
        pass

    def onKeyDown(self, key):
        pass

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h
        self.x = x
        self.y = y

    def render(self, canvas, x, y):
        filler = ' ' * self.width
        title = ' ' + self.title
        title = '\033[5;30;47m' + (title + filler[:-len(title)]) + '\033[0m'  # noqa
        canvas.append('\033[{1};{0}H{2}'.format(x, y, title))


class Footer(object):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.title = 'debug '
        self.events = []
        subscribe('event', self.onMessage)

    def onMessage(self, event):
        self.events.append(event)
        if len(self.events) > 10:
            self.events.pop(0)

        publish('repaint')

    def onScroll(self, direction):
        pass

    def onKeyDown(self, key):
        pass

    def onResize(self, x, y, w, h):
        self.width = w
        self.height = h
        self.x = x
        self.y = y

    def render(self, canvas, x, y):
        filler = ' ' * self.width
        title = '\033[7;32m ' + self.title + '\033[0;31m ' + ', '.join(reversed(self.events))  # noqa
        title = title + filler[:-len(title)]
        title = title[:min(self.width, len(title))] + '\033[0m'
        canvas.append('\033[{1};{0}H{2}'.format(x, self.height - 1 + self.y, title))  # noqa


def main():
    # screen bleeding and multiline strings test
    # big_data = [' B-{0}'.format('{0}'.format(i % 10) * ((i + 1) % 200)) for i in range(0, 1000, 1)]  # noqa

    # screen buffer seek test
    big_data = [' B-{0}'.format(i + 1) for i in range(0, 2000, 1)]

    # 100MB data test
    # big_data = [bytes("1")] * 5 * 10**7

    # with open("100MB.txt", "w") as text_file:
    # text_file.write('\n'.join(big_data))

    header = Header()
    header.height = 2

    footer = Footer()
    footer.height = 2

    left_list = VerticalScrollableScreen([
        'Item 1',
        'Item 2',
        'Item 3'
    ])
    left_list.width = 50

    screen = VerticalSplitScreen(
        top=header,
        bottom=VerticalSplitScreen(
            top=HorizontalSplitScreen(
                left=left_list,
                right=VerticalScrollableScreen(big_data),
            ),
            bottom=footer
        )
    )

    start(screen)

if __name__ == '__main__':
    main()
