# -*- coding: utf-8 -*-
from datetime import datetime

import re


# Example log line, to understand the regex below (truncated to fit into
# 80 chars):
#
# Dec  9 13:01:26 localhost haproxy[28029]: 127.0.0.1:39759
# [09/Dec/2013:12:59:46.633] loadbalancer default/instance8
# 0/51536/1/48082/99627 200 83285 - - ---- 87/87/87/1/0 0/67
# {77.24.148.74} "GET /path/to/image HTTP/1.1"
HAPROXY_LINE_REGEX = re.compile(
    # Dec  9 13:01:26
    r'\A\w+\s+\d+\s+\d+:\d+:\d+\s+'  # syslog date, ignored
    # localhost haproxy[28029]:
    r'\w+\s+\w+\[\d+\]:\s+'  # haproxy process name and pid, ignored
    # 127.0.0.1:39759
    r'(?P<client_ip>(\d+\.){3}\d+):(?P<client_port>\d+)\s+'
    # [09/Dec/2013:12:59:46.633]
    r'\[(?P<accept_date>.*)\..*\]\s+'
    # loadbalancer default/instance8
    r'(?P<frontend_name>.*)\s+(?P<backend_name>.*)/(?P<server_name>.*)\s+'
    # 0/51536/1/48082/99627
    r'(?P<tq>-?\d+)/(?P<tw>-?\d+)/(?P<tc>-?\d+)/'
    r'(?P<tr>-?\d+)/(?P<tt>\+?\d+)\s+'
    # 200 83285
    r'(?P<status_code>\d+)\s+(?P<bytes_read>\+?\d+)\s+'
    # - - ----
    r'.*\s+'  # ignored by now, should capture cookies and termination state
    # 87/87/87/1/0
    r'(?P<act>\d+)/(?P<fe>\d+)/(?P<be>\d+)/'
    r'(?P<srv>\d+)/(?P<retries>\+?\d+)\s+'
    # 0/67
    r'(?P<queue_server>\d+)/(?P<queue_backend>\d+)\s+'
    # {77.24.148.74}
    r'((?P<request_headers>{.*})\s+(?P<response_headers>{.*})\s+|'
    r'(?P<headers>{.*})\s+|)'
    # "GET /path/to/image HTTP/1.1"
    r'"(?P<http_request>.*)"'
    r'\Z'  # end of line
)

HTTP_REQUEST_REGEX = re.compile(
    r'(?P<method>\w+)\s+'
    r'(?P<path>(/[/\w:,;\.#$!?=&@%_+\'\*~|\(\)\[\]-]+)+)'
    r'\s+(?P<protocol>\w+/\d\.\d)'
)


class HaproxyLogLine(object):

    def __init__(self, line):
        """For a description of every field see:
        http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#8.2.3

        The declarations here follow the syntax of the log file, thus
        backend_name is found after fronted_name and before server_name.

        This helps keeping an eye on where a specific field is stored.
        """
        self.client_ip = None
        self.client_port = None

        # raw string from log line and its python datetime version
        self.raw_accept_date = None
        self.accept_date = None

        self.frontend_name = None
        self.backend_name = None
        self.server_name = None

        self.time_wait_request = None
        self.time_wait_queues = None
        self.time_connect_server = None
        self.time_wait_response = None
        self.total_time = None

        self.status_code = None
        self.bytes_read = None

        # not used by now
        self.captured_request_cookie = None
        self.captured_response_cookie = None

        # not used by now
        self.termination_state = None

        self.connections_active = None
        self.connections_frontend = None
        self.connections_backend = None
        self.connections_server = None
        self.retries = None

        self.queue_server = None
        self.queue_backend = None

        self.captured_request_headers = None
        self.captured_response_headers = None

        self.raw_http_request = None
        self.http_request_method = None
        self.http_request_path = None
        self.http_request_protocol = None

        self.raw_line = line

        self.valid = self._parse_line(line)

    def _parse_line(self, line):
        matches = HAPROXY_LINE_REGEX.match(line)
        if matches is None:
            return False

        self.client_ip = matches.group('client_ip')
        self.client_port = int(matches.group('client_port'))

        self.raw_accept_date = matches.group('accept_date')
        self.accept_date = self._parse_accept_date()

        self.frontend_name = matches.group('frontend_name')
        self.backend_name = matches.group('backend_name')
        self.server_name = matches.group('server_name')

        self.time_wait_request = int(matches.group('tq'))
        self.time_wait_queues = int(matches.group('tw'))
        self.time_connect_server = int(matches.group('tc'))
        self.time_wait_response = int(matches.group('tr'))
        self.total_time = matches.group('tt')

        self.status_code = matches.group('status_code')
        self.bytes_read = matches.group('bytes_read')

        self.connections_active = matches.group('act')
        self.connections_frontend = matches.group('fe')
        self.connections_backend = matches.group('be')
        self.connections_server = matches.group('srv')
        self.retries = matches.group('retries')

        self.queue_server = int(matches.group('queue_server'))
        self.queue_backend = int(matches.group('queue_backend'))

        self.captured_request_headers = matches.group('request_headers')
        self.captured_response_headers = matches.group('response_headers')
        if matches.group('headers') is not None:
            self.captured_request_headers = matches.group('headers')

        self.raw_http_request = matches.group('http_request')
        self._parse_http_request()

        return True

    def _parse_accept_date(self):
        return datetime.strptime(self.raw_accept_date, '%d/%b/%Y:%H:%M:%S')

    def _parse_http_request(self):
        matches = HTTP_REQUEST_REGEX.match(self.raw_http_request)
        if matches:
            self.http_request_method = matches.group('method')
            self.http_request_path = matches.group('path')
            self.http_request_protocol = matches.group('protocol')
