from datetime import datetime
from multiprocessing import Pool

from haproxy.line import parse_line
from haproxy.utils import date_str_to_datetime, delta_str_to_timedelta


class Log:
    def __init__(self, logfile=None, start=None, delta=None, show_invalid=False):
        self.logfile = logfile
        self.show_invalid = show_invalid
        self.start = None
        self.end = None

        if start:
            self.start = date_str_to_datetime(start)

        if delta:
            delta = delta_str_to_timedelta(delta)

            if isinstance(self.start, datetime):
                self.end = self.start + delta

        self.invalid_lines = 0
        self.valid_lines = 0

    def __iter__(self):
        start = datetime.now()
        with open(self.logfile) as logfile, Pool() as pool:
            for index, line in enumerate(pool.imap(parse_line, logfile)):
                if line.is_valid:
                    self.valid_lines += 1
                    if line.is_within_time_frame(self.start, self.end):
                        yield line
                else:
                    if self.show_invalid:
                        print(line.raw_line)
                    self.invalid_lines += 1

                if index % 10000 == 0 and index > 0:  # pragma: no cover
                    print('.', end='', flush=True)

        end = datetime.now()
        print(f'\nIt took {end - start}')

    @property
    def total_lines(self):
        return self.valid_lines + self.invalid_lines
