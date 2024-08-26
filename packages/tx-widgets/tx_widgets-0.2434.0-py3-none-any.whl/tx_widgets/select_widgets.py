from operator import methodcaller
from re import compile, IGNORECASE

from pybrary import fuzzy_select
from .select_base import SelectWidget


class SelectContains(SelectWidget):
    def select(self, selector):
        return [i for i in self.entries if selector in i]


class SelectInsensitive(SelectWidget):
    def select(self, selector):
        return [i for i in self.entries if selector in i.lower()]


class SelectRex(SelectWidget):
    def select(self, selector):
        rex = compile(selector, IGNORECASE).match
        return [i for i in self.entries if rex(i)]


class SelectFuzzy(SelectWidget):
    def select(self, selector):
        return fuzzy_select(selector, self.entries, decorate=methodcaller('lower'))
