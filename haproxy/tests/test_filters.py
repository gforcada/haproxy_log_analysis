# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy import filters
from haproxy.line import Line
from haproxy.tests.test_log_line import LogLineBaseTest


class FiltersTest(LogLineBaseTest):

    def test_filter_ip(self):
        """Check that filter_ip filter works as expected."""
        ip_one = '1.2.3.4'
        ip_two = '2.3.4.5'
        self.headers = ' {{{0}}} '.format(ip_one)
        raw_line = self._build_test_string()
        log_line = Line(raw_line)

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
            log_line = Line(raw_line)

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
            log_line = Line(raw_line)

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
            log_line = Line(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, True, ])

    def test_filter_slow_requests(self):
        """Check that filter_slow_requests filter works as expected."""
        filter_func = filters.filter_slow_requests('10000')

        results = []
        for response_time in (45, 13000, 4566):
            self.tr = response_time
            raw_line = self._build_test_string()
            log_line = Line(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [False, True, False, ])

    def test_filter_wait_on_queues(self):
        """Check that filter_wait_on_queues filter works as expected"""
        filter_func = filters.filter_wait_on_queues('50')

        results = []
        for waiting_time in (45, 13000, 4566):
            self.tw = waiting_time
            raw_line = self._build_test_string()
            log_line = Line(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, False, ])

    def test_str_to_timedelta(self):
        """Check that deltas are converted to timedelta objects."""
        data = filters._delta_str_to_timedelta('45s')
        self.assertEqual(timedelta(seconds=45), data)

        data = filters._delta_str_to_timedelta('2m')
        self.assertEqual(timedelta(minutes=2), data)

        data = filters._delta_str_to_timedelta('13h')
        self.assertEqual(timedelta(hours=13), data)

        data = filters._delta_str_to_timedelta('1d')
        self.assertEqual(timedelta(days=1), data)

    def test_str_to_datetime(self):
        """Check that start are converted to datetime objects."""
        data = filters._date_str_to_datetime('11/Dec/2013')
        self.assertEqual(datetime(2013, 12, 11), data)

        data = filters._date_str_to_datetime('11/Dec/2013:13')
        self.assertEqual(datetime(2013, 12, 11, hour=13), data)

        data = filters._date_str_to_datetime('11/Dec/2013:14:15')
        self.assertEqual(datetime(2013, 12, 11, hour=14, minute=15), data)

        data = filters._date_str_to_datetime('11/Dec/2013:14:15:16')
        self.assertEqual(datetime(2013, 12, 11, hour=14, minute=15, second=16),
                         data)

    def test_filter_time_frame_no_limit(self):
        """Test that if empty strings are passed to filter_time_frame all log
        lines are accepted.
        """
        filter_func = filters.filter_time_frame('', '')

        results = []
        for accept_date in ('09/Dec/2013:10:53:42.33',
                            '19/Jan/2014:12:39:16.63',
                            '29/Jun/2012:15:27:23.66'):
            self.accept_date = accept_date
            raw_line = self._build_test_string()
            log_line = Line(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, True, True, ])

    def test_filter_time_frame_only_start(self):
        """Test that if empty strings are passed to filter_time_frame all log
        lines are accepted.
        """
        filter_func = filters.filter_time_frame('3/Oct/2013', '')

        results = []
        for accept_date in ('09/Dec/2013:10:53:42.33',
                            '19/Jan/2014:12:39:16.63',
                            '29/Jun/2012:15:27:23.66'):
            self.accept_date = accept_date
            raw_line = self._build_test_string()
            log_line = Line(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [True, True, False, ])

    def test_filter_time_frame_start_and_delta(self):
        """Test that if empty strings are passed to filter_time_frame all log
        lines are accepted.
        """
        filter_func = filters.filter_time_frame('29/Jun/2012:15', '30m')

        results = []
        for accept_date in ('09/Dec/2013:10:53:42.33',
                            '19/Jan/2014:12:39:16.63',
                            '29/Jun/2012:15:27:23.66'):
            self.accept_date = accept_date
            raw_line = self._build_test_string()
            log_line = Line(raw_line)

            results.append(filter_func(log_line))

        self.assertEqual(results, [False, False, True, ])

    def test_filter_status_code(self):
        """Test that the status_code filter works as expected."""
        filter_func = filters.filter_status_code('404')

        self.status = '404'
        raw_line = self._build_test_string()
        log_line = Line(raw_line)
        self.assertTrue(filter_func(log_line))

        self.status = '200'
        raw_line = self._build_test_string()
        log_line = Line(raw_line)
        self.assertFalse(filter_func(log_line))

    def test_filter_status_code_family(self):
        """Test that the status_code_family filter works as expected."""
        filter_func = filters.filter_status_code_family('4')

        results = []
        for status in ('404', '503', '401', ):
            self.status = status
            raw_line = self._build_test_string()
            log_line = Line(raw_line)
            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, True, ])

    def test_filter_http_method(self):
        """Test that the http_method filter works as expected."""
        filter_func = filters.filter_http_method('GET')

        results = []
        for http_method in ('GET', 'POST', 'PUT', 'GET', ):
            self.http_request = '{0} /something HTTP/1.1'.format(http_method)
            raw_line = self._build_test_string()
            log_line = Line(raw_line)
            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, False, True, ])

    def test_filter_backend(self):
        """Test that the backend filter works as expected."""
        filter_func = filters.filter_backend('default')

        results = []
        for backend_name in ('default', 'anonymous', 'registered', ):
            self.backend_name = backend_name
            raw_line = self._build_test_string()
            log_line = Line(raw_line)
            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, False, ])

    def test_filter_frontend(self):
        """Test that the frontend filter works as expected."""
        filter_func = filters.filter_frontend('loadbalancer')

        results = []
        for frontend_name in ('loadbalancer', 'other', 'loadbalancer', ):
            self.frontend_name = frontend_name
            raw_line = self._build_test_string()
            log_line = Line(raw_line)
            results.append(filter_func(log_line))

        self.assertEqual(results, [True, False, True, ])

    def test_filter_server(self):
        """Test that the server filter works as expected."""
        filter_func = filters.filter_server('instance8')

        results = []
        for server_name in ('instance7', 'instance', 'instance8', ):
            self.server_name = server_name
            raw_line = self._build_test_string()
            log_line = Line(raw_line)
            results.append(filter_func(log_line))

        self.assertEqual(results, [False, False, True, ])

    def test_filter_response_size(self):
        """Test that the size filter works as expected."""
        # does not matter if the filter parameter has a leading sign plus
        # or not, it should return the same results.
        filter_func_1 = filters.filter_response_size('400')
        filter_func_2 = filters.filter_response_size('+400')

        results_1 = []
        results_2 = []
        for size in ('300', '+399', '+598', '401', ):
            self.bytes = size
            raw_line = self._build_test_string()
            log_line = Line(raw_line)
            results_1.append(filter_func_1(log_line))
            results_2.append(filter_func_2(log_line))

        self.assertEqual(results_1, [False, False, True, True, ])
        self.assertEqual(results_1, results_2)
