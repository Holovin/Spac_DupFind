import re

from datetime import date, datetime, timedelta, time


class SpacDate:
    month = [" ", "янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
    re_date = re.compile('(\d{1,2})\s(.{1,3})\s(\d{4})?')
    re_time = re.compile('(\d{2}):(\d{2})')

    @staticmethod
    def _month_to_int(text):
        return SpacDate.month.index(text)

    def _string_to_date(self, text):
        # convert date like "1 июл 2014" or "1 июл" to date(...)
        r = self.re_date.search(text)

        if r is None:
            return date.today()

        day = int(r.group(1))
        month = SpacDate._month_to_int(r.group(2))
        year = datetime.now().year

        if r.group(3):
            year = int(r.group(3))

        return date(year, month, day)

    def _string_to_time(self, text):
        # convert time like "00:00" to time(...)
        r = self.re_time.search(text)

        if r is None:
            return time()

        return time(int(r.group(1)), int(r.group(2)))

    def get_python_time(self, text):
        # yesterday like "вчера в 00:00"
        if "вчера " in text:
            yesterday = date.today() - timedelta(1)
            t = self._string_to_time(text)

            return datetime.combine(yesterday, t)

        # today like "в 00:00"; any past date like "1 июл в 00:00" or "1 июл 2010"
        d = self._string_to_date(text)
        t = self._string_to_time(text)

        return datetime.combine(d, t)
