# -*- coding: utf-8 -*-
from haproxy.haproxy_logline import HaproxyLogLine


class HaproxyLogFile(object):

    def __init__(self, logfile=None, start=None, delta=None):
        self.logfile = logfile
        self.start = start
        self.delta = delta

        self.total_lines = None

        self._valid_lines = []
        self._invalid_lines = []

    def parse_file(self):
        if self.logfile is None:
            raise ValueError('No log file is configured yet!')

        with open(self.logfile) as logfile:
            for line in logfile:
                self.total_lines += 1
                stripped_line = line.strip()
                parsed_line = HaproxyLogLine(stripped_line)
                if parsed_line.valid:
                    self._valid_lines.append(parsed_line)
                else:
                    self._invalid_lines.append(stripped_line)

    @classmethod
    def commands(cls):
        """Returns a list of all methods that start with cmd_"""
        cmds = [cmd[4:] for cmd in dir(cls) if cmd.startswith('cmd_')]
        return cmds

    def cmd_counter(self):
        return len(self._valid_lines)

    def cmd_counter_invalid(self):
        return len(self._invalid_lines)

    def cmd_http_methods(self):
        pass
