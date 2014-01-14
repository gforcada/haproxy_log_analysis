# -*- coding: utf-8 -*-
from haproxy import filters
from haproxy.haproxy_logline import HaproxyLogLine
from haproxy.tests.test_haproxy_log_line import HaproxyLogLineTest


class FiltersTest(HaproxyLogLineTest):

    def test_filter_ip(self):
        """Check that filter_ip filter works as expected."""
        ip_one = '1.2.3.4'
        ip_two = '2.3.4.5'
        self.headers = ' {{{0}}} '.format(ip_one)
        raw_line = self._build_test_string()
        log_line = HaproxyLogLine(raw_line)

        filter_func_ip_one = filters.filter_ip(ip_one)
        filter_func_ip_two = filters.filter_ip(ip_two)

        self.assertTrue(filter_func_ip_one(log_line))
        self.assertFalse(filter_func_ip_two(log_line))

    def test_filter_ip_range(self):
        """Check that filter_ip_range filter works as expected."""
        filter_func = filters.filter_ip_range('1.2.3')

        ips = ('1.2.3.4', '2.3.4.5', '1.2.3.6', )
        results = []
        for ip in ips:
            self.headers = ' {{{0}}} '.format(ip)
            raw_line = self._build_test_string()
            log_line = HaproxyLogLine(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, True, ])

    def test_filter_path(self):
        """Check that filter_path filter works as expected."""
        filter_func = filters.filter_path('/image')
        method = 'GET'
        protocol = 'HTTP/1.1'

        paths = ('/path/to/image', '/something/else', '/another/image/here', )
        results = []
        for path in paths:
            self.http_request = '{0} {1} {2}'.format(method, path, protocol)
            raw_line = self._build_test_string()
            log_line = HaproxyLogLine(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, True, ])

    def test_filter_ssl(self):
        """Check that filter_path filter works as expected."""
        filter_func = filters.filter_ssl()
        method = 'GET'
        protocol = 'HTTP/1.1'

        paths = ('/ssl_path:443/image',
                 '/something/else',
                 '/another:443/ssl', )
        results = []
        for path in paths:
            self.http_request = '{0} {1} {2}'.format(method, path, protocol)
            raw_line = self._build_test_string()
            log_line = HaproxyLogLine(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, True, ])

