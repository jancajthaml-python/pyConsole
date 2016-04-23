# import gevent

from pyConsole import VerticalSplitScreen
from pyConsole import HorizontalSplitScreen
from pyConsole import VerticalScrollableScreen
from pyConsole import init
from pyConsole import resize
from pyConsole import start
from pyConsole import publish
from pyConsole import subscribe


class Menu(VerticalScrollableScreen):

    def onKeyDown(self, key):
        if self.focus:
            if key == '\n':
                publish('build_screen', self.selected)


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


if __name__ == '__main__':
    # screen bleeding and multiline strings test
    # big_data = [' B-{0}'.format('{0}'.format(i % 10) * ((i + 1) % 200)) for i in range(0, 1000, 1)]  # noqa

    # screen buffer seek test
    big_data = [
        {
            'id': 'line_{0}'.format(i + 1),
            'label': 'Line number {0}'.format(i + 1)
        } for i in range(0, 2000, 1)
    ]

    menu_items = [
        {
            'id': 'item_1',
            'label': 'Item 1'
        },
        {
            'id': 'item_2',
            'label': 'Item 2'
        },
        {
            'id': 'item_3',
            'label': 'Item 3'
        },
        {
            'id': 'item_4',
            'label': 'Item 4'
        }
    ]
    header = Header()
    header.height = 2

    footer = Footer()
    footer.height = 2

    left_list = Menu(menu_items)
    left_list.width = 10

    def build_screen(item):
        selected_item = menu_items[next(index for (index, d) in enumerate(menu_items) if d['id'] == item)]  # noqa

        # label = menu_items[]
        big_data = [
            {
                'id': '{0}_line_{1}'.format(selected_item['id'], i + 1),
                'label': '{0} -> {1}'.format(selected_item['label'], i + 1)
            } for i in range(0, 2000, 1)
        ]
        publish('set_screen', VerticalSplitScreen(
            top=header,
            bottom=VerticalSplitScreen(
                top=HorizontalSplitScreen(
                    left=left_list,
                    right=VerticalScrollableScreen(big_data),
                ),
                bottom=footer
            )
        ))
        resize()

    init()

    subscribe('build_screen', build_screen)

    publish('build_screen', 'item_1')

    start()
