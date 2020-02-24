from datetime import datetime, timedelta

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

        self._relative = False
        self._exact_time = True

        self.discarded = []

    def reset(self):
        self._day = 0
        self._month = 0
        self._year = 0
        self._hour = 0
        self._minute = 0
        self._root = None
        self._relative = False
        self._exact_time = False
        self.discarded = []

    def parse(self, text):
        self.reset()

        tree = self.parser.parse(text)

        self.check_root(tree)

        if self._relative:
            days = self._day
            if self._month:
                days += 30 * self._month

            if self._exact_time:
                delta = timedelta(days=days)
                return datetime.utcnow().replace(hour=self._hour, minute=self._minute) + delta
            else:
                delta = timedelta(days=days, minutes=self._minute, hours=self._hour)
                return datetime.utcnow() + delta
        else:
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

            if child.data.startswith('rel'):
                self.check_relative(child)
                self._relative = True

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

        time_type = tree.children[0]

        for child in time_type.children:
            if child.data == 'meridiem':
                hour = int(child.children[0].value)
                minute = int(child.children[1].value)
                
                if child.children[-1].startswith('post'):
                    hour += 12
            else: # military
                hour = int(child.children[0].value)
                minute = int(child.children[1].value)

            self._hour = hour
            self._minute = minute
            self._exact_time = True

    def check_relative(self, tree):
        if tree.data.startswith('rel_'):
            val = 0
            if 'one' in tree.data:
                val = 1
            else:
                val = int(tree.children[0].value)

            if 'minute' in tree.data:
                self._minute = val
            elif 'hour' in tree.data:
                self._hour = val
            elif 'day' in tree.data:
                self._day = val
            elif 'week' in tree.data:
                self._day = val * 7
            elif 'month' in tree.data:
                self._month = val
            elif 'year' in tree.data:
                self._year = val
        else:
            for child in tree.children:
                if child.data == 'yesterday':
                    self._day = -1
                elif child.data == 'today':
                    self._day = 0
                elif child.data == 'tomorrow':
                    self._day = 1
