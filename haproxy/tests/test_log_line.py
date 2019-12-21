# -*- coding: utf-8 -*-
from datetime import datetime
from haproxy.line import Line

import unittest


# 8 and 9 parameters are together because if no headers are saved the field
# is completely empty and thus there is no double space between queue backend
# and http request.
LINE = '{0} {1} {2} [{3}] {4} {5} {6} - - ---- {7} {8}{9} "{10}"'


class LogLineBaseTest(unittest.TestCase):
    def setUp(self):
        self.syslog_date = 'Dec  9 13:01:26'
        self.process_name_and_pid = 'localhost haproxy[28029]:'

        self.client_ip = '127.0.0.1'
        self.client_port = 2345

        self.accept_date = '09/Dec/2013:12:59:46.633'

        self.frontend_name = 'loadbalancer'
        self.backend_name = 'default'
        self.server_name = 'instance8'

        self.tq = 0
        self.tw = 51536
        self.tc = 1
        self.tr = 48082
        self.tt = '99627'

        self.status = '200'
        self.bytes = '83285'

        self.act = '87'
        self.fe = '89'
        self.be = '98'
        self.srv = '1'
        self.retries = '20'

        self.queue_server = 2
        self.queue_backend = 67
        self.headers = ' {77.24.148.74}'
        self.http_request = 'GET /path/to/image HTTP/1.1'

    def _build_test_string(self):
        client_ip_and_port = f'{self.client_ip}:{self.client_port}'
        server_names = f'{self.frontend_name} {self.backend_name}/{self.server_name}'
        timers = f'{self.tq}/{self.tw}/{self.tc}/{self.tr}/{self.tt}'
        status_and_bytes = f'{self.status} {self.bytes}'
        connections_and_retries = (
            f'{self.act}/{self.fe}/{self.be}/{self.srv}/{self.retries}'
        )
        queues = f'{self.queue_server}/{self.queue_backend}'

        log_line = LINE.format(
            self.syslog_date,
            self.process_name_and_pid,
            client_ip_and_port,
            self.accept_date,
            server_names,
            timers,
            status_and_bytes,
            connections_and_retries,
            queues,
            self.headers,
            self.http_request,
        )
        return Line(log_line)


class LogLineTest(LogLineBaseTest):
    def test_default_values(self):
        log_line = self._build_test_string()

        self.assertEqual(self.client_ip, log_line.client_ip)
        self.assertEqual(self.client_port, log_line.client_port)

        self.assertTrue(log_line.raw_accept_date in self.accept_date)

        self.assertEqual(self.frontend_name, log_line.frontend_name)
        self.assertEqual(self.backend_name, log_line.backend_name)
        self.assertEqual(self.server_name, log_line.server_name)

        self.assertEqual(self.tq, log_line.time_wait_request)
        self.assertEqual(self.tw, log_line.time_wait_queues)
        self.assertEqual(self.tc, log_line.time_connect_server)
        self.assertEqual(self.tr, log_line.time_wait_response)
        self.assertEqual(self.tt, log_line.total_time)

        self.assertEqual(self.status, log_line.status_code)
        self.assertEqual(self.bytes, log_line.bytes_read)

        self.assertEqual(self.act, log_line.connections_active)
        self.assertEqual(self.fe, log_line.connections_frontend)
        self.assertEqual(self.be, log_line.connections_backend)
        self.assertEqual(self.srv, log_line.connections_server)
        self.assertEqual(self.retries, log_line.retries)

        self.assertEqual(self.queue_server, log_line.queue_server)
        self.assertEqual(self.queue_backend, log_line.queue_backend)

        self.assertEqual(self.headers.strip(), log_line.captured_request_headers)
        self.assertEqual(None, log_line.captured_response_headers)

        self.assertEqual(self.http_request, log_line.raw_http_request)

        self.assertTrue(log_line.valid)

    def test_unused_values(self):
        log_line = self._build_test_string()

        self.assertEqual(log_line.captured_request_cookie, None)
        self.assertEqual(log_line.captured_response_cookie, None)
        self.assertEqual(log_line.termination_state, None)

    def test_datetime_value(self):
        log_line = self._build_test_string()
        self.assertTrue(isinstance(log_line.accept_date, datetime))

    def test_http_request_values(self):
        method = 'GET'
        path = '/path/to/image'
        protocol = 'HTTP/1.1'
        self.http_request = '{0} {1} {2}'.format(method, path, protocol)
        log_line = self._build_test_string()

        self.assertEqual(log_line.http_request_method, method)
        self.assertEqual(log_line.http_request_path, path)
        self.assertEqual(log_line.http_request_protocol, protocol)

    def test_invalid(self):
        """Check that if a log line can not be parsed with the regular
        expression, 'valid' is False.
        """
        self.bytes = 'wrooooong'
        log_line = self._build_test_string()
        self.assertFalse(log_line.valid)

    def test_no_captured_headers(self):
        """Check that if a log line does not have any captured headers, the
        line is still valid.
        """
        self.headers = ''
        log_line = self._build_test_string()
        self.assertTrue(log_line.valid)

    def test_request_and_response_captured_headers(self):
        """Check that if a log line does have both request and response headers
        captured, both are parsed correctly.
        """
        request_headers = '{something}'
        response_headers = '{something_else}'
        self.headers = ' {0} {1}'.format(request_headers, response_headers)
        log_line = self._build_test_string()

        self.assertTrue(log_line.valid)
        self.assertEqual(log_line.captured_request_headers, request_headers)
        self.assertEqual(log_line.captured_response_headers, response_headers)

    def test_request_is_https_valid(self):
        """Check that if a log line contains the SSL port on it, is reported
        as a https connection.
        """
        self.http_request = 'GET /domain:443/to/image HTTP/1.1'
        log_line = self._build_test_string()
        self.assertTrue(log_line.is_https())

    def test_request_is_https_false(self):
        """Check that if a log line does not contains the SSL port on it, is
        not reported as a https connection.
        """
        self.http_request = 'GET /domain:80/to/image HTTP/1.1'
        log_line = self._build_test_string()
        self.assertFalse(log_line.is_https())

    def test_request_is_front_page(self):
        """Check that if a request is for the front page the request path is
        correctly stored.
        """
        self.http_request = 'GET / HTTP/1.1'
        log_line = self._build_test_string()
        self.assertEqual('/', log_line.http_request_path)

    def test_strip_syslog_valid_hostname_slug(self):
        """Checks that if the hostname added to syslog slug is still valid line"""
        self.http_request = 'GET / HTTP/1.1'
        self.process_name_and_pid = 'ip-192-168-1-1 haproxy[28029]:'
        log_line = self._build_test_string()
        self.assertTrue(log_line.valid)

    def test_unparseable_http_request(self):
        self.http_request = 'something'
        log_line = self._build_test_string()
        self.assertEqual(log_line.http_request_method, 'invalid')
        self.assertEqual(log_line.http_request_path, 'invalid')
        self.assertEqual(log_line.http_request_protocol, 'invalid')

    def test_dot_on_process_name(self):
        """Checks that process names can have a dot on it"""
        self.process_name_and_pid = 'localhost.localdomain haproxy[2345]:'
        log_line = self._build_test_string()
        self.assertTrue(log_line.valid)

    def test_nixos_syslog(self):
        """Check that the NixOS timestamp at the beginning can also be parsed
        """
        self.syslog_date = '2017-07-06T14:29:39+02:00'
        log_line = self._build_test_string()
        self.assertTrue(log_line.valid)
