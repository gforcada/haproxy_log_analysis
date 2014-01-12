# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta
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
        """Returns a list of all methods that start with ``cmd_``."""
        cmds = [cmd[4:] for cmd in dir(cls) if cmd.startswith('cmd_')]
        return cmds

    def cmd_counter(self):
        """Returns the number of valid lines."""
        return len(self._valid_lines)

    def cmd_counter_invalid(self):
        """Returns the number of invalid lines."""
        return len(self._invalid_lines)

    def cmd_http_methods(self):
        """Reports a breakdown of how many requests have been made per HTTP
        method (GET, POST...).
        """
        methods = defaultdict(int)
        for line in self._valid_lines:
            methods[line.http_request_method] += 1
        return methods

    def cmd_ip_counter(self):
        """Reports a breakdown of how many requests have been made per IP.

        .. note::
          To enable this command requests need to provide a header with the
          forwarded IP (usually X-Forwarded-For) and be it the only header
          being captured.
        """
        ip_counter = defaultdict(int)
        for line in self._valid_lines:
            if line.captured_request_headers is not None:
                stripped_brackets = line.captured_request_headers[1:-1]
                ip_counter[stripped_brackets] += 1
        return ip_counter

    def cmd_top_ips(self):
        """Returns the top most frequent IPs.

        .. note::
          See ``_sort_and_trim`` for its current limitations.
        """
        return self._sort_and_trim(
            self.cmd_ip_counter(),
            reverse=True
        )

    def cmd_status_codes_counter(self):
        """Generate statistics about HTTP status codes. 404, 500 and so on.
        """
        status_codes = defaultdict(int)
        for line in self._valid_lines:
            status_codes[line.status_code] += 1
        return status_codes

    def cmd_request_path_counter(self):
        """Generate statistics about HTTP requests' path."""
        paths = defaultdict(int)
        for line in self._valid_lines:
            paths[line.http_request_path] += 1
        return paths

    def cmd_top_request_paths(self):
        """Returns the top most frequent paths.

        .. note::
          See ``_sort_and_trim`` for its current limitations.
        """
        return self._sort_and_trim(
            self.cmd_request_path_counter(),
            reverse=True
        )

    def cmd_slow_requests(self):
        """List all requests that took a certain amount of time to be
        processed.

        .. warning::
           By now hardcoded to 1 second (1000 milliseconds), improve the
           command line interface to allow to send parameters to each command
           or globally.
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

    def cmd_queue_peaks(self):
        """Generate a list of the requests peaks on the queue.

        A queue peak is defined by the biggest value on the backend queue
        on a series of log lines that are between log lines without being
        queued.

        .. warning::
          Allow to configure up to which peak can be ignored. Currently
          set to 1.
        """
        threshold = 1
        peaks = []
        current_peak = 0
        queue = 0

        for line in self._valid_lines:
            queue = line.queue_backend

            if queue == 0 and current_peak > threshold:
                peaks.append(current_peak)
                current_peak = 0

            if queue > current_peak:
                current_peak = queue

        # case of a series that does not end
        if queue > 0 and current_peak > threshold:
            peaks.append(current_peak)

        return peaks

    def cmd_connection_type(self):
        """Generates statistics on how many requests are made via HTTP and how
        many are made via SSL.

        .. note::
          This only works if the request path contains the default port for
          SSL (443).

        .. warning::
          The ports are hardcoded, they should be configurable.
        """
        https = 0
        non_https = 0
        for line in self._valid_lines:
            if line.is_https():
                https += 1
            else:
                non_https += 1
        return https, non_https

    def cmd_requests_per_minute(self):
        """Generates statistics on how many requests were made per minute.

        .. note::
          Try to combine it with time constrains (``-s`` and ``-d``) as this
          command output can be huge if not.
        """
        if len(self._valid_lines) == 0:
            return

        current_minute = self._valid_lines[0].accept_date
        current_minute_counter = 0
        requests = []
        one_minute = timedelta(minutes=1)

        def format_and_append(append_to, date, counter):
            seconds_and_micro = timedelta(
                seconds=date.second,
                microseconds=date.microsecond
            )
            minute_formatted = date - seconds_and_micro
            append_to.append((minute_formatted, counter))

        # note that _valid_lines is kept sorted by date
        for line in self._valid_lines:
            line_date = line.accept_date
            if line_date - current_minute < one_minute and \
                    line_date.minute == current_minute.minute:
                current_minute_counter += 1

            else:
                format_and_append(
                    requests,
                    current_minute,
                    current_minute_counter
                )
                current_minute_counter = 1
                current_minute = line_date

        if current_minute_counter > 0:
            format_and_append(
                requests,
                current_minute,
                current_minute_counter
            )

        return requests

    def _is_in_time_range(self, log_line):
        """'log_line' is in time range if there is a time range to begin with
        and the 'log_line' time is within 'start_time' and 'end_time'.
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

    @staticmethod
    def _sort_and_trim(data, reverse=False):
        """Sorts a dictionary with at least two fields on each of them sorting
        by the second element.

        .. warning::
          Right now is hardcoded to 10 paths, improve the command line
          interface to allow to send parameters to each command or globally.
        """
        threshold = 10
        data_list = data.items()
        data_list = sorted(data_list,
                           key=lambda data_info: data_info[1],
                           reverse=reverse)
        return data_list[:threshold]
