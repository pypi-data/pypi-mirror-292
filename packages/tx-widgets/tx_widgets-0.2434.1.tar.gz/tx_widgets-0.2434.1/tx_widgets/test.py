from textual import on
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Label

from select_widgets import (
    SelectWidget,
    SelectContains,
    SelectInsensitive,
    SelectRex,
    SelectFuzzy as Selector,
)


class WidgetTest(App):
    CSS = '''
        Select {
            width: 1fr;
        }
    '''
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    def compose(self):
        with Horizontal():
            yield Selector([
                'Banane',
                'Trompette',
                'Kiwi',
                'Raquette',
                'Bougie',
            ])
            with Vertical():
                yield Label('', id='highlighted')
                yield Static('', id='selected')

    @on(SelectWidget.UpdateHighlighted)
    def highlight(self, event):
        event.stop()
        self.query_one('#highlighted').update(event.value)

    @on(SelectWidget.UpdateSelected)
    def select(self, event):
        event.stop()
        self.query_one('#selected').update(event.value)


if __name__=='__main__': WidgetTest().run()
