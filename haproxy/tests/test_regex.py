# -*- coding: utf-8 -*-
from datetime import datetime
from haproxy.haproxy import HAPROXY_LINE_REGEX

import unittest


LINE = '{0} {1} {2} [{3}] {4} {5} {6} - - ---- {7} {8} {9} "{10}"'


class HaproxyLogLineRegexTest(unittest.TestCase):

    def setUp(self):
        self.syslog_date = 'Dec  9 13:01:26'
        self.process_name_and_pid = 'localhost haproxy[28029]:'
        self.client_ip_and_port = '127.0.0.1:39759'
        self.accept_date = '09/Dec/2013:12:59:46.633'
        self.server_names = 'loadbalancer default/instance8'
        self.timers = '0/51536/1/48082/99627'
        self.status_and_bytes = '200 83285'
        self.connections_and_retries = '87/87/87/1/0'
        self.queues = '0/67'
        self.headers = '{77.24.148.74}'
        self.http_request = 'GET /path/to/image HTTP/1.1'

    def _build_test_string(self):
        log_line = LINE.format(
            self.syslog_date,
            self.process_name_and_pid,
            self.client_ip_and_port,
            self.accept_date,
            self.server_names,
            self.timers,
            self.status_and_bytes,
            self.connections_and_retries,
            self.queues,
            self.headers,
            self.http_request,
        )
        return log_line

    def test_line_regex_default_values(self):
        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('http_request'), self.http_request)

    def test_line_regex_client_ip_and_port(self):
        client_ip = '192.168.0.250'
        client_port = '34'
        self.client_ip_and_port = '{0}:{1}'.format(client_ip, client_port)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('client_ip'), client_ip)
        self.assertEqual(matches.group('client_port'), client_port)

    def test_line_regex_accept_date(self):
        self.accept_date = datetime.now().strftime('%d/%b/%Y:%H:%M:%S.%f')

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertTrue(matches.group('accept_date') in self.accept_date)

    def test_line_regex_server_names(self):
        frontend_name = 'SomeThing4'
        backend_name = 'Another1'
        server_name = 'Cloud9'
        self.server_names = '{0} {1}/{2}'.format(
            frontend_name, backend_name, server_name
        )

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('frontend_name'), frontend_name)
        self.assertEqual(matches.group('backend_name'), backend_name)
        self.assertEqual(matches.group('server_name'), server_name)

    def test_line_regex_timers(self):
        tq = '23'
        tw = '0'
        tc = '3'
        tr = '4'
        tt = '5'
        self.timers = '{0}/{1}/{2}/{3}/{4}'.format(tq, tw, tc, tr, tt)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('tq'), tq)
        self.assertEqual(matches.group('tw'), tw)
        self.assertEqual(matches.group('tc'), tc)
        self.assertEqual(matches.group('tr'), tr)
        self.assertEqual(matches.group('tt'), tt)

    def test_line_regex_timers_with_sign(self):
        tq = '-23'
        tw = '-10'
        tc = '-3'
        tr = '-4'
        tt = '+5'
        self.timers = '{0}/{1}/{2}/{3}/{4}'.format(tq, tw, tc, tr, tt)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('tq'), tq)
        self.assertEqual(matches.group('tw'), tw)
        self.assertEqual(matches.group('tc'), tc)
        self.assertEqual(matches.group('tr'), tr)
        self.assertEqual(matches.group('tt'), tt)

    def test_line_regex_status_and_bytes(self):
        status = '23'
        bytes_read = '10'
        self.status_and_bytes = '{0} {1}'.format(status, bytes_read)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('status_code'), status)
        self.assertEqual(matches.group('bytes_read'), bytes_read)

    def test_line_regex_status_and_bytes_with_sign(self):
        status = '404'
        bytes_read = '+10'
        self.status_and_bytes = '{0} {1}'.format(status, bytes_read)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('status_code'), status)
        self.assertEqual(matches.group('bytes_read'), bytes_read)

    def test_line_regex_connections_and_retries(self):
        act = '40'
        fe = '10'
        be = '11'
        srv = '12'
        retries = '14'
        self.connections_and_retries = '{0}/{1}/{2}/{3}/{4}'.format(
            act, fe, be, srv, retries,
        )

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('act'), act)
        self.assertEqual(matches.group('fe'), fe)
        self.assertEqual(matches.group('be'), be)
        self.assertEqual(matches.group('srv'), srv)
        self.assertEqual(matches.group('retries'), retries)

    def test_line_regex_connections_and_retries_with_sign(self):
        act = '30'
        fe = '0'
        be = '111'
        srv = '412'
        retries = '+314'
        self.connections_and_retries = '{0}/{1}/{2}/{3}/{4}'.format(
            act, fe, be, srv, retries,
        )

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('act'), act)
        self.assertEqual(matches.group('fe'), fe)
        self.assertEqual(matches.group('be'), be)
        self.assertEqual(matches.group('srv'), srv)
        self.assertEqual(matches.group('retries'), retries)

    def test_line_regex_queues(self):
        server = '30'
        backend = '0'
        self.queues = '{0}/{1}'.format(server, backend)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('queue_server'), server)
        self.assertEqual(matches.group('queue_backend'), backend)

    def test_line_regex_headers_empty(self):
        self.headers = ''

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('request_headers'), None)
        self.assertEqual(matches.group('response_headers'), None)

    def test_line_regex_headers(self):
        request = 'something in the air'
        response = 'something not in the air'
        self.headers = '{{{0}}} {{{1}}}'.format(request, response)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertTrue(request in matches.group('request_headers'))
        self.assertTrue(response in matches.group('response_headers'))

    def test_line_regex_headers_only_one(self):
        request = 'something in the air'
        self.headers = '{{{0}}}'.format(request)

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('request_headers'), None)
        self.assertEqual(matches.group('response_headers'), None)
        self.assertTrue(request in matches.group('headers'))

    def test_line_regex_http_request(self):
        http_request = 'something in the air'
        self.http_request = http_request

        log_line = self._build_test_string()
        matches = HAPROXY_LINE_REGEX.match(log_line)

        self.assertEqual(matches.group('http_request'), http_request)
