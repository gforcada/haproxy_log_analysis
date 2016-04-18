# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta
from haproxy.line import Line

import os


# compatibility code for python 2 and python 3 differences
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Log(object):

    def __init__(self, logfile=None):
        self.logfile = logfile
        self._pickle_file = '{0}.pickle'.format(logfile)
        # only this attributes will be pickled
        self._pickle_attributes = ['_valid_lines',
                                   '_invalid_lines',
                                   'total_lines', ]

        self.total_lines = 0

        self._valid_lines = []
        self._invalid_lines = []
        if self.logfile:
            self.parse_file()

    def parse_file(self):
        if self._is_pickle_valid():
            self._load()
        else:
            with open(self.logfile) as logfile:
                self.parse_data(logfile)
                self._sort_lines()
                self._save()

    def _is_pickle_valid(self):
        """Logic to decide if the file should be processed or just needs to
        be loaded from its pickle data.
        """
        if not os.path.exists(self._pickle_file):
            return False
        else:
            file_mtime = os.path.getmtime(self.logfile)
            pickle_mtime = os.path.getmtime(self._pickle_file)
            if file_mtime > pickle_mtime:
                return False
        return True

    def _load(self):
        """Load data from a pickle file. """
        with open(self._pickle_file, 'rb') as source:
            pickler = pickle.Unpickler(source)

            for attribute in self._pickle_attributes:
                pickle_data = pickler.load()
                setattr(self, attribute, pickle_data)

    def _save(self):
        """Save the attributes defined on _pickle_attributes in a pickle file.

        This improves a lot the nth run as the log file does not need to be
        processed every time.
        """
        with open(self._pickle_file, 'wb') as source:
            pickler = pickle.Pickler(source, pickle.HIGHEST_PROTOCOL)

            for attribute in self._pickle_attributes:
                attr = getattr(self, attribute, None)
                pickler.dump(attr)

    def parse_data(self, logfile):
        """Parse data from data stream and replace object lines.

        :param logfile: [required] Log file data stream.
        :type logfile: str
        """

        for line in logfile:
            self.total_lines += 1
            stripped_line = line.strip()
            parsed_line = Line(stripped_line)

            if parsed_line.valid:
                self._valid_lines.append(parsed_line)
            else:
                self._invalid_lines.append(stripped_line)

    def filter(self, filter_func, reverse=False):
        """Filter current log lines by a given filter function.

        This allows to drill down data out of the log file by filtering the
        relevant log lines to analyze.

        For example, filter by a given IP so only log lines for that IP are
        further processed with commands (top paths, http status counter...).

        :param filter_func: [required] Filter method, see filters.py for all
          available filters.
        :type filter_func: function
        :param reverse: negate the filter (so accept all log lines that return
          ``False``).
        :type reverse: boolean
        :returns: a new instance of Log containing only log lines
          that passed the filter function.
        :rtype: :class:`Log`

        TODO:
            Deep copy implementation.
        """
        new_log_file = Log()
        new_log_file.logfile = self.logfile

        new_log_file.total_lines = 0

        new_log_file._valid_lines = []
        new_log_file._invalid_lines = self._invalid_lines[:]

        # add the reverse conditional outside the loop to keep the loop as
        # straightforward as possible
        if not reverse:
            for i in self._valid_lines:
                if filter_func(i):
                    new_log_file.total_lines += 1
                    new_log_file._valid_lines.append(i)
        else:
            for i in self._valid_lines:
                if not filter_func(i):
                    new_log_file.total_lines += 1
                    new_log_file._valid_lines.append(i)

        return new_log_file

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
            ip = line.get_ip()
            if ip is not None:
                ip_counter[ip] += 1
        return ip_counter

    def cmd_top_ips(self):
        """Returns the top most frequent IPs.

        .. note::
          See :meth:`.Log._sort_and_trim` for its current
          limitations.
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
          See :meth:`.Log._sort_and_trim` for its current
          limitations.
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
        slow_requests = [line.time_wait_response for line in self._valid_lines
                         if line.time_wait_response > 1000]
        return slow_requests

    def cmd_average_response_time(self):
        """Returns the average response time of all, non aborted, requests."""
        average = [line.time_wait_response for line in self._valid_lines
                   if line.time_wait_response >= 0]

        divisor = float(len(average))
        if divisor > 0:
            return sum(average) / float(len(average))
        return 0

    def cmd_average_waiting_time(self):
        """Returns the average queue time of all, non aborted, requests."""
        average = [line.time_wait_queues for line in self._valid_lines
                   if line.time_wait_queues >= 0]

        divisor = float(len(average))
        if divisor > 0:
            return sum(average) / float(len(average))
        return 0

    def cmd_counter_slow_requests(self):
        """Counts all requests that took a certain amount of time to be
        processed.

        .. warning::
           By now hardcoded to 1 second (1000 milliseconds), improve the
           command line interface to allow to send parameters to each command
           or globally.
        """
        return len(self.cmd_slow_requests())

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
        current_queue = 0

        current_span = 0
        first_on_queue = None

        for line in self._valid_lines:
            current_queue = line.queue_backend

            if current_queue > 0:
                current_span += 1

                if first_on_queue is None:
                    first_on_queue = line.accept_date

            if current_queue == 0 and current_peak > threshold:
                peaks.append({'peak': current_peak,
                              'span': current_span,
                              'first': first_on_queue,
                              'last': line.accept_date, })
                current_peak = 0
                current_span = 0
                first_on_queue = None

            if current_queue > current_peak:
                current_peak = current_queue

        # case of a series that does not end
        if current_queue > 0 and current_peak > threshold:
            peaks.append({'peak': current_peak,
                          'span': current_span,
                          'first': first_on_queue,
                          'last': line.accept_date, })

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
          command output can be huge otherwise.
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

    def cmd_print(self):
        """Returns the raw lines to be printed."""
        data = ''
        for line in self._valid_lines:
            data += line.raw_line
            data += '\n'

        return data

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
          Right now is hardcoded to 10 elements, improve the command line
          interface to allow to send parameters to each command or globally.
        """
        threshold = 10
        data_list = data.items()
        data_list = sorted(data_list,
                           key=lambda data_info: data_info[1],
                           reverse=reverse)
        return data_list[:threshold]
