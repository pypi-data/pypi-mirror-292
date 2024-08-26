from textual import on
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, OptionList


class SelectWidget(Widget):
    DEFAULT_CSS = """
        #fuzzy_input{
            align-vertical: top;
        }
        #fuzzy_entries{
            height: 80%;
            align-vertical: top;
        }
    """

    class UpdateHighlighted(Message):
        def __init__(self, options, value):
            self.options = options
            self.value = value
            super().__init__()

        @property
        def control(self):
            return self.options

    class UpdateSelected(Message):
        def __init__(self, options, value):
            self.options = options
            self.value = value
            super().__init__()

        @property
        def control(self):
            return self.options

    def __init__(self, entries, **k):
        super().__init__(**k)
        self.entries = list(entries)
        self.highlighted = None
        self.selected = None

    def select(self, selector):
        raise NotImplementedError

    def filter_entries(self, selector=None):
        if selector:
            try:
                return self.select(selector)
            except Exception: pass
        return self.entries

    def compose(self):
        with Vertical(id='fuzzy_container'):
            self.input = Input(placeholder='fuzzy', id='fuzzy_input')
            self.options = OptionList(*self.filter_entries(), id='fuzzy_entries')
            yield self.input
            yield self.options

    @on(Input.Changed, '#fuzzy_input')
    def change_event(self, event):
        selector = self.input.value
        self.options.clear_options()
        found = self.filter_entries(selector)
        if found:
            self.options.add_options(found)
            self.selected = found[0]
            self.highlighted = found[0]
        else:
            self.selected = ''
            self.highlighted = ''
        self.post_message(self.UpdateHighlighted(self.options, self.highlighted))

    @on(Input.Submitted, '#fuzzy_input')
    def submit_event(self, event):
        event.stop()
        self.post_message(self.UpdateSelected(self, self.selected))

    @on(OptionList.OptionHighlighted, '#fuzzy_entries')
    def highlight_event(self, event):
        event.stop()
        self.highlighted = event.option.prompt
        self.post_message(self.UpdateHighlighted(self.options, self.highlighted))

    @on(OptionList.OptionSelected, '#fuzzy_entries')
    def select_event(self, event):
        event.stop()
        self.selected = event.option.prompt
        self.post_message(self.UpdateSelected(self.options, self.selected))
