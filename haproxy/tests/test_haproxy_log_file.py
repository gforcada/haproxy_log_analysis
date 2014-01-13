# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy.haproxy_logfile import HaproxyLogFile
from haproxy.main import create_parser
from haproxy.main import main

import unittest


class HaproxyLogFileTest(unittest.TestCase):

    def test_haproxy_log_file_from_main(self):
        start = datetime.now()
        delta = timedelta(1)
        filename = 'haproxy/tests/files/small.log'
        data = {
            'start': start,
            'delta': delta,
            'filename': filename,
            'commands': ['counter', ],
            'list_commands': False,
        }
        parser = create_parser()
        logfile = main(data, parser)

        self.assertEqual(logfile.start_time, start)
        self.assertEqual(logfile.delta, delta)
        self.assertEqual(logfile.end_time, start + delta)
        self.assertEqual(logfile.logfile, filename)

    def test_haproxy_log_file_error_no_file(self):
        """Check that trying to parse a non existing file raises an error."""
        log_file = HaproxyLogFile()
        with self.assertRaises(ValueError):
            log_file.parse_file()

    def test_haproxy_log_file_parsed(self):
        """Check that log files are parsed"""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log'
        )
        self.assertEqual(log_file.cmd_counter(), 0)
        log_file.parse_file()
        self.assertTrue(log_file.cmd_counter() > 0)

    def test_haproxy_log_file_total_lines(self):
        """Check that even if some lines are not valid, 'total_lines' counts
        all of them.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/2_ok_1_invalid.log'
        )
        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 3)

    def test_haproxy_log_file_valid_and_invalid_lines(self):
        """Check that if some log lines can not be parsed both numbers are
        correctly reported.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/2_ok_1_invalid.log'
        )
        log_file.parse_file()
        self.assertEqual(log_file.cmd_counter(), 2)
        self.assertEqual(log_file.cmd_counter_invalid(), 1)

    def test_haproxy_log_file_attributes_start_and_end_time(self):
        """Check that both 'start_time' and 'end_time' are correct."""
        now = datetime.now()
        one_day = timedelta(days=1)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/2_ok_1_invalid.log',
            start=now,
            delta=one_day,
        )
        self.assertEqual(log_file.start_time, now)
        self.assertEqual(log_file.end_time, now + one_day)

    def test_haproxy_log_file_attributes_start_and_end_time_no_value(self):
        """Check that both 'start_time' and 'end_time' are None if no value
        is passed on HaproxyLogFile __init__ method.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/2_ok_1_invalid.log'
        )
        self.assertEqual(log_file.start_time, None)
        self.assertEqual(log_file.end_time, None)

    def test_haproxy_log_file_attributes_start_time_no_delta(self):
        """Check how 'start_time', 'delta' and 'end_time' attributes are
        set as they should if only start time is given.
        """
        now = datetime.now()
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/2_ok_1_invalid.log',
            start=now,
        )
        self.assertEqual(log_file.start_time, now)
        self.assertEqual(log_file.delta, None)
        self.assertEqual(log_file.end_time, None)

    def test_haproxy_log_file_start_time_no_results(self):
        """Check that if the start time is after all log entries, no log
        entries are considered.
        """
        after_log_entries = datetime(year=2013, month=12, day=13)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/times.log',
            start=after_log_entries,
        )
        self.assertEqual(log_file.start_time, after_log_entries)
        self.assertEqual(log_file.delta, None)
        self.assertEqual(log_file.end_time, None)

        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 9)
        self.assertEqual(log_file.cmd_counter(), 0)
        self.assertEqual(log_file.cmd_counter_invalid(), 0)

    def test_haproxy_log_file_start_time_some_results(self):
        """Check that if the start time is between some log entries, the log
        entries are considered.
        """
        between_log_entries = datetime(year=2013, month=12, day=10)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/times.log',
            start=between_log_entries,
        )
        self.assertEqual(log_file.start_time, between_log_entries)
        self.assertEqual(log_file.delta, None)
        self.assertEqual(log_file.end_time, None)

        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 9)
        self.assertEqual(log_file.cmd_counter(), 6)
        self.assertEqual(log_file.cmd_counter_invalid(), 0)

    def test_haproxy_log_file_start_time_and_end_time_some_results(self):
        """Check that if the start time is between some log entries and there
        is a end_time, the entries that fit in are counted.
        """
        between_log_entries = datetime(year=2013, month=12, day=9, hour=11)
        one_day = timedelta(days=1)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/times.log',
            start=between_log_entries,
            delta=one_day,
        )
        self.assertEqual(log_file.start_time, between_log_entries)
        self.assertEqual(log_file.delta, one_day)
        self.assertEqual(log_file.end_time, between_log_entries + one_day)

        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 9)
        self.assertEqual(log_file.cmd_counter(), 3)
        self.assertEqual(log_file.cmd_counter_invalid(), 0)

    def test_haproxy_log_file_lines_sorted(self):
        """Check that after parsing a log file, the valid log lines are kept
        sorted to ease further work on them.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()

        previous = log_file._valid_lines[0]
        previous_date = previous.accept_date
        for line in log_file._valid_lines[1:]:
            self.assertTrue(previous_date < line.accept_date)

    def test_haproxy_log_file_cmd_http_methods(self):
        """Check that the http methods command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()
        http_methods = log_file.cmd_http_methods()

        self.assertEqual(len(http_methods), 3)
        self.assertEqual(http_methods['GET'], 4)
        self.assertEqual(http_methods['POST'], 2)
        self.assertEqual(http_methods['HEAD'], 3)

    def test_haproxy_log_file_cmd_ip_counter(self):
        """Check that the ip counter command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()
        ip_counter = log_file.cmd_ip_counter()

        self.assertEqual(len(ip_counter), 4)
        self.assertEqual(ip_counter['123.123.123.123'], 4)
        self.assertEqual(ip_counter['123.123.124.124'], 2)
        self.assertEqual(ip_counter['123.123.124.123'], 1)
        self.assertEqual(ip_counter['123.123.123.124'], 1)

    def test_haproxy_log_file_cmd_status_codes(self):
        """Check that the status codes command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()
        status_codes = log_file.cmd_status_codes_counter()

        self.assertEqual(len(status_codes), 3)
        self.assertEqual(status_codes['404'], 3)
        self.assertEqual(status_codes['200'], 2)
        self.assertEqual(status_codes['300'], 4)

    def test_haproxy_log_file_cmd_request_path_counter(self):
        """Check that the request path counter command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()
        path_counter = log_file.cmd_request_path_counter()

        self.assertEqual(len(path_counter), 5)
        self.assertEqual(path_counter['/hello'], 3)
        self.assertEqual(path_counter['/world'], 2)
        self.assertEqual(path_counter['/free'], 2)
        self.assertEqual(path_counter['/fra'], 1)
        self.assertEqual(path_counter['/freitag'], 1)

    def test_haproxy_log_file_cmd_slow_requests(self):
        """Check that the slow requests counter command reports as
        expected.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()
        slow_requests = log_file.cmd_slow_requests()

        self.assertEqual(len(slow_requests), 5)
        slow_requests.sort()  # sort them as the log analyzer sorts by dates
        self.assertEqual(slow_requests,
                         [1293, 2936, 2942, 20095, 29408, ])

    def test_haproxy_log_file_cmd_server_load(self):
        """Check that the server load counter command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/small.log',
        )
        log_file.parse_file()
        servers = log_file.cmd_server_load()

        self.assertEqual(len(servers), 3)
        self.assertEqual(servers['instance1'], 4)
        self.assertEqual(servers['instance2'], 3)
        self.assertEqual(servers['instance3'], 2)

    def test_haproxy_log_file_cmd_queue_peaks(self):
        """Check that the queue peaks command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/queue.log',
        )
        log_file.parse_file()
        peaks = log_file.cmd_queue_peaks()

        self.assertEqual(len(peaks), 4)
        self.assertEqual(peaks[0]['peak'], 4)
        self.assertEqual(peaks[0]['span'], 5)

        self.assertEqual(peaks[1]['peak'], 19)
        self.assertEqual(peaks[1]['span'], 5)

        self.assertEqual(peaks[2]['peak'], 49)
        self.assertEqual(peaks[2]['span'], 3)

        self.assertEqual(peaks[3]['peak'], 3)
        self.assertEqual(peaks[3]['span'], 1)

        self.assertTrue(peaks[0]['first'] < peaks[1]['first'])
        self.assertTrue(peaks[1]['first'] < peaks[2]['first'])
        self.assertTrue(peaks[2]['first'] < peaks[3]['first'])

        self.assertTrue(peaks[0]['last'] < peaks[1]['last'])
        self.assertTrue(peaks[1]['last'] < peaks[2]['last'])
        self.assertTrue(peaks[2]['last'] < peaks[3]['last'])

    def test_haproxy_log_file_cmd_queue_peaks_no_end(self):
        """Check that the queue peaks command reports as expected when the
        last log request did not have any queue.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/queue_2.log',
        )
        log_file.parse_file()
        peaks = log_file.cmd_queue_peaks()

        self.assertEqual(len(peaks), 3)
        self.assertEqual(peaks[0]['peak'], 4)
        self.assertEqual(peaks[0]['span'], 5)

        self.assertEqual(peaks[1]['peak'], 19)
        self.assertEqual(peaks[1]['span'], 5)

        self.assertEqual(peaks[2]['peak'], 49)
        self.assertEqual(peaks[2]['span'], 3)

        self.assertTrue(peaks[0]['first'] < peaks[1]['first'])
        self.assertTrue(peaks[1]['first'] < peaks[2]['first'])

        self.assertTrue(peaks[0]['last'] < peaks[1]['last'])
        self.assertTrue(peaks[1]['last'] < peaks[2]['last'])

    def test_haproxy_log_file_cmd_top_ips(self):
        """Check that the top ips command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/top_ips.log',
        )
        log_file.parse_file()
        top_ips = log_file.cmd_top_ips()

        self.assertEqual(len(top_ips), 10)
        self.assertEqual(top_ips[0], ('1.1.1.15', 6))
        self.assertEqual(top_ips[1], ('1.1.1.11', 5))

        # as the 3rd and 4th have the same repetitions their order is unknown
        self.assertEqual(top_ips[2][1], 4)
        self.assertEqual(top_ips[3][1], 4)
        self.assertTrue(top_ips[2][0] in ('1.1.1.10', '1.1.1.19'))
        self.assertTrue(top_ips[3][0] in ('1.1.1.10', '1.1.1.19'))

        # the same as above for all the others
        other_ips = [
            '1.1.1.12',
            '1.1.1.13',
            '1.1.1.14',
            '1.1.1.16',
            '1.1.1.17',
            '1.1.1.18',
        ]
        for ip_info in top_ips[4:]:
            self.assertEqual(ip_info[1], 2)
            self.assertTrue(ip_info[0] in other_ips)

            # remove the other_ips to ensure all ips are there
            for position, current in enumerate(other_ips):
                if current == ip_info[0]:
                    del other_ips[position]
                    break

        self.assertEqual(other_ips, [])

    def test_haproxy_log_file_cmd_top_request_paths(self):
        """Check that the top request paths command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/top_paths.log',
        )
        log_file.parse_file()
        top_paths = log_file.cmd_top_request_paths()

        self.assertEqual(len(top_paths), 10)
        self.assertEqual(top_paths[0], ('/14', 6))
        self.assertEqual(top_paths[1], ('/13', 4))

        # as the 3rd and 4th have the same repetitions their order is unknown
        self.assertEqual(top_paths[2][1], 3)
        self.assertEqual(top_paths[3][1], 3)
        self.assertEqual(top_paths[4][1], 3)
        self.assertTrue(top_paths[2][0] in ('/12', '/15', '/11', ))
        self.assertTrue(top_paths[3][0] in ('/12', '/15', '/11', ))
        self.assertTrue(top_paths[4][0] in ('/12', '/15', '/11', ))

        # the same as above for all the others
        other_paths = [
            '/1',
            '/2',
            '/3',
            '/4',
            '/5',
            '/6',
            '/7',
            '/8',
            '/9',
        ]
        for path_info in top_paths[5:]:
            self.assertEqual(path_info[1], 2)
            self.assertTrue(path_info[0] in other_paths)

            # remove the other_ips to ensure all ips are there
            for position, current in enumerate(other_paths):
                if current == path_info[0]:
                    del other_paths[position]
                    break

        self.assertEqual(len(other_paths), 4)

    def test_haproxy_log_file_cmd_connection_type(self):
        """Check that the connection type command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/connection.log',
        )
        log_file.parse_file()
        ssl, non_ssl = log_file.cmd_connection_type()

        self.assertEqual(ssl, 7)
        self.assertEqual(non_ssl, 5)

    def test_haproxy_log_file_cmd_requests_per_minute(self):
        """Check that the requests per minute command reports as expected."""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/requests_per_minute.log',
        )
        log_file.parse_file()
        requests = log_file.cmd_requests_per_minute()

        self.assertEqual(len(requests), 5)

        self.assertEqual(
            requests[0],
            (datetime(2013, 12, 11, 11, 2), 8)
        )
        self.assertEqual(
            requests[1],
            (datetime(2013, 12, 11, 11, 3), 3)
        )
        self.assertEqual(
            requests[2],
            (datetime(2013, 12, 11, 11, 13), 5)
        )
        self.assertEqual(
            requests[3],
            (datetime(2013, 12, 11, 11, 52), 7)
        )
        self.assertEqual(
            requests[4],
            (datetime(2013, 12, 11, 12, 2), 9)
        )

    def test_haproxy_log_file_cmd_requests_per_minute_no_lines(self):
        """Check that the requests per minute command reports nothing if there
        are no valid lines to check for.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/requests_per_minute.log',
            start=datetime(2014, 3, 18)
        )
        log_file.parse_file()
        requests = log_file.cmd_requests_per_minute()

        self.assertEqual(requests, None)
