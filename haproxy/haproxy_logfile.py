# -*- coding: utf-8 -*-
from collections import defaultdict
from haproxy.haproxy_logline import HaproxyLogLine


class HaproxyLogFile(object):

    def __init__(self, logfile=None, start=None, delta=None):
        self.logfile = logfile
        self.start_time = start
        self.delta = delta

        self.end_time = None
        if self.start_time is not None and self.delta is not None:
            self.end_time = start + delta

        self.total_lines = 0

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

                if not parsed_line.valid:
                    self._invalid_lines.append(stripped_line)
                elif self._is_in_time_range(parsed_line):
                    self._valid_lines.append(parsed_line)

        self._sort_lines()

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
        methods = defaultdict(int)
        for line in self._valid_lines:
            methods[line.http_request_method] += 1
        return methods

    def cmd_ip_counter(self):
        """To enable this command requests need to provide a header with the
        forwarded IP (usually X-Forwarded-For) and be it the only header
        being captured.
        """
        ip_counter = defaultdict(int)
        for line in self._valid_lines:
            if line.captured_request_headers is not None:
                stripped_brackets = line.captured_request_headers[1:-1]
                ip_counter[stripped_brackets] += 1
        return ip_counter

    def cmd_status_codes_counter(self):
        """Generate statistics about HTTP status codes. 404, 500 and so on.
        """
        status_codes = defaultdict(int)
        for line in self._valid_lines:
            status_codes[line.status_code] += 1
        return status_codes

    def cmd_request_path_counter(self):
        """Generate statistics about HTTP requests path."""
        paths = defaultdict(int)
        for line in self._valid_lines:
            paths[line.http_request_path] += 1
        return paths

    def cmd_slow_requests(self):
        """List all requests that took a certain amount of time to be
        processed.

        TODO: by now hardcoded to 1 second (1000 milliseconds), improve the
        command line interface to allow to send parameters to each command or
        globally.
        """
        slow_requests = []
        for line in self._valid_lines:
            response_time = line.time_wait_response
            if response_time > 1000:
                slow_requests.append(response_time)
        return slow_requests

    def cmd_server_load(self):
        """Generate statistics regarding how many requests were processed by
        each downstream server.
        """
        servers = defaultdict(int)
        for line in self._valid_lines:
            servers[line.server_name] += 1
        return servers

    def _is_in_time_range(self, log_line):
        """'log_line' is in time range if there is a time range to begin with
        and the 'log_line' time is within 'start_time' and 'end_time'
        """
        if self.start_time is None:
            return True
        elif self.start_time > log_line.accept_date:
            return False

        if self.end_time is None:
            return True
        elif self.end_time < log_line.accept_date:
            return False

        return True

    def _sort_lines(self):
        """Haproxy writes its logs after having gathered all information
        related to each specific connection. A simple request can be
        really quick but others can be really slow, thus even if one connection
        is logged later, it could have been accepted before others that are
        already processed and logged.

        This method sorts all valid log lines by their acceptance date,
        providing the real order in which connections where made to the server.
        """
        self._valid_lines = sorted(self._valid_lines,
                                   key=lambda line: line.accept_date)
