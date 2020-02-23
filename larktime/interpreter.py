from datetime import datetime

from lark import Lark
from pathlib import Path

DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
MONTHS = ['__', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

class DateTimeParser:
    def __init__(self):
        grammar = Path(__file__).parent.joinpath('datetime.lark')

        self.parser = Lark.open(grammar, parser='lalr', start='_expr')

        self._day = 0
        self._month = 0
        self._year = 0
        self._hour = 0
        self._minute = 0
        self._root = None

        self.discarded = []

    def parse(self, text):
        tree = self.parser.parse(text)

        self.check_root(tree)

        return datetime(self._year, self._month, self._day, self._hour, self._minute)

    def check_root(self, tree):
        self._root = tree

        for child in tree.children:
            if child.data == 'random':
                self.discarded.append(child.children[0].value)
                continue

            if child.data == 'date':
                self.check_date(child)
            
            if child.data == 'time':
                self.check_time(child)

    def check_date(self, tree):
        day_next = False

        for child in tree.children:
            if child.data in ['other', 'little_endian', 'middle_endian', 'on_clause']:
                return self.check_date(child)

            if child.data in DAYS:
                day_next = True
                continue

            if day_next:
                self._day = int(child.children[0].value)
                day_next = False
                continue

            if child.data == 'ord_ind':
                continue

            if child.data in MONTHS:
                self._month = MONTHS.index(child.data)

            if child.data == 'year':
                self._year = int(child.children[0].value)

    def check_time(self, tree):
        hour_found = False

        for child in tree.children:
            if child.data == 'hour_min':
                if hour_found:
                    self._minute = int(child.children[0].value)
                else:
                    hour_found = True
                    self._hour = int(child.children[0].value)
