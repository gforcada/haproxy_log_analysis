# -*- coding: utf-8 -*-
from datetime import datetime
from haproxy.line import Line
from haproxy.utils import delta_str_to_timedelta
from haproxy.utils import date_str_to_datetime


class Log(object):
    def __init__(self, logfile=None, start=None, delta=None):
        self.logfile = logfile
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
        with open(self.logfile) as logfile:
            for line in logfile:
                parsed_line = self.parse_line(line)
                if parsed_line:
                    yield parsed_line

    def parse_line(self, line):
        stripped_line = line.strip()
        parsed_line = Line(stripped_line)

        if parsed_line.is_valid and parsed_line.is_within_time_frame(
            self.start, self.end
        ):
            self.valid_lines += 1
            return parsed_line
        else:
            self.invalid_lines += 1

    @property
    def total_lines(self):
        return self.valid_lines + self.invalid_lines
