from datetime import datetime, timedelta

import pytest

from haproxy import commands


def check_output(cmd, output, expected, capsys):
    """Validate the output of commands."""
    name = cmd.command_line_name().upper()
    cmd.results(output=output)
    output_text = capsys.readouterr().out
    if output == 'json':
        assert f'{{"{name}": {expected}}}' in output_text
    else:
        assert f'{name}\n====' in output_text
        assert f'====\n{expected}\n' in output_text


@pytest.mark.parametrize(
    'klass, expected',
    [
        (commands.StatusCodesCounter, 'status_codes_counter'),
        (commands.AverageResponseTime, 'average_response_time'),
        (commands.Counter, 'counter'),
        (commands.IpCounter, 'ip_counter'),
    ],
)
def test_commands_names(klass, expected):
    """Check that the command line name of command classes are generated correctly."""
    assert klass.command_line_name() == expected


def test_counter_results():
    """Test the Counter command.

    It plain and simply counts all the lines passed to it.
    """
    cmd = commands.Counter()
    assert cmd.raw_results() == 0
    for x in range(3):
        cmd(x)

    assert cmd.raw_results() == 3


@pytest.mark.parametrize('output', [None, 'json'])
def test_counter_output(capsys, output):
    """Test the Counter command.

    It plain and simply counts all the lines passed to it.
    """
    cmd = commands.Counter()
    for x in range(3):
        cmd(x)
    check_output(cmd, output, 3, capsys)


def test_http_methods_results(line_factory):
    """Test the HTTPMethods command.

    It creates a breakdown of how many times each HTTP verb has been used.
    """
    cmd = commands.HttpMethods()
    assert cmd.raw_results() == {}
    for verb, count in (('POST', 4), ('GET', 3), ('PUT', 2)):
        line = line_factory(http_request=f'{verb} /path/to/image HTTP/1.1')
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 3
    assert results['POST'] == 4
    assert results['GET'] == 3
    assert results['PUT'] == 2


@pytest.mark.parametrize(
    'output, expected',
    [(None, '- PUT: 2\n- GET: 1'), ('json', '[{"PUT": 2}, {"GET": 1}]')],
)
def test_http_methods_output(line_factory, capsys, output, expected):
    """Test the HTTPMethods command.

    It creates a breakdown of how many times each HTTP verb has been used.
    """
    cmd = commands.HttpMethods()
    for verb, count in (('GET', 1), ('PUT', 2)):
        line = line_factory(http_request=f'{verb} /path/to/image HTTP/1.1')
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_ip_counter_results(line_factory):
    """Test the IpCounter command.

    It creates a breakdown of how many times each IP has been used.
    """
    cmd = commands.IpCounter()
    assert cmd.raw_results() == {}
    for ip, count in (('192.168.0.1', 4), ('172.4.3.2', 3), ('8.7.6.5', 2)):
        line = line_factory(headers=f' {{{ip}}}')
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 3
    assert results['192.168.0.1'] == 4
    assert results['172.4.3.2'] == 3
    assert results['8.7.6.5'] == 2


@pytest.mark.parametrize(
    'output, expected',
    [
        (None, '- 172.4.3.2: 3\n- 8.7.6.5: 2'),
        ('json', '[{"172.4.3.2": 3}, {"8.7.6.5": 2}]'),
    ],
)
def test_ip_counter_output(line_factory, capsys, output, expected):
    """Test the IpCounter command.

    It creates a breakdown of how many times each IP has been used.
    """
    cmd = commands.IpCounter()
    for ip, count in (('172.4.3.2', 3), ('8.7.6.5', 2)):
        line = line_factory(headers=f' {{{ip}}}')
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_top_ips_results(line_factory):
    """Test the TopIps command.

    It lists the 10 most used IPs, and how much where they used.
    """
    cmd = commands.TopIps()
    assert cmd.raw_results() == []
    for ip, count in ((f'192.168.0.{x}', x) for x in range(11)):
        line = line_factory(headers=f' {{{ip}}}')
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 10
    assert results[0] == ('192.168.0.10', 10)
    assert results[1] == ('192.168.0.9', 9)
    assert results[2] == ('192.168.0.8', 8)
    assert results[3] == ('192.168.0.7', 7)
    assert results[4] == ('192.168.0.6', 6)
    assert results[5] == ('192.168.0.5', 5)
    assert results[6] == ('192.168.0.4', 4)
    assert results[7] == ('192.168.0.3', 3)
    assert results[8] == ('192.168.0.2', 2)
    assert results[9] == ('192.168.0.1', 1)


def test_top_ips_print_results(line_factory):
    """Test the TopIps command.

    Ensure that when they are printed, only 10 results are shown.
    """
    cmd = commands.TopIps()
    for ip, count in ((f'192.168.0.{x}', x) for x in range(14)):
        line = line_factory(headers=f' {{{ip}}}')
        for _ in range(count):
            cmd(line)
    results = cmd.print_data()
    results = [x for x in results.split('\n') if x]
    assert len(results) == 10
    assert results[0] == '- 192.168.0.13: 13'
    assert results[-1] == '- 192.168.0.4: 4'


@pytest.mark.parametrize(
    'output, expected',
    [
        (None, '- 192.168.0.2: 2\n- 192.168.0.1: 1'),
        ('json', '[{"192.168.0.2": 2}, {"192.168.0.1": 1}]'),
    ],
)
def test_top_ips_output(line_factory, capsys, output, expected):
    """Test the TopIps command.

    It lists the 10 most used IPs, and how much where they used.
    """
    cmd = commands.TopIps()
    assert cmd.raw_results() == []
    for ip, count in ((f'192.168.0.{x}', x) for x in range(3)):
        line = line_factory(headers=f' {{{ip}}}')
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_status_codes_counter_results(line_factory):
    """Test the StatusCodesCounter command.

    It creates a breakdown of which status codes have been used and how many each.
    """
    cmd = commands.StatusCodesCounter()
    assert cmd.raw_results() == {}
    for status_code, count in (('200', 4), ('301', 3), ('500', 2)):
        line = line_factory(status=status_code)
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 3
    assert results['200'] == 4
    assert results['301'] == 3
    assert results['500'] == 2


@pytest.mark.parametrize(
    'output, expected',
    [(None, '- 301: 3\n- 500: 2'), ('json', '[{"301": 3}, {"500": 2}]')],
)
def test_status_codes_counter_output(line_factory, capsys, output, expected):
    """Test the StatusCodesCounter command.

    It creates a breakdown of which status codes have been used and how many each.
    """
    cmd = commands.StatusCodesCounter()
    for status_code, count in (('301', 3), ('500', 2)):
        line = line_factory(status=status_code)
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_request_path_counter_results(line_factory):
    """Test the RequestPathCounter command.

    It creates a breakdown of how many times each URL path has been used.
    """
    cmd = commands.RequestPathCounter()
    assert cmd.raw_results() == {}
    for path, count in (('/image/one', 4), ('/video/two', 3), ('/article/three', 2)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 3
    assert results['/image/one'] == 4
    assert results['/video/two'] == 3
    assert results['/article/three'] == 2


@pytest.mark.parametrize(
    'output, expected',
    [
        (None, '- /video/two: 3\n- /article/three: 2'),
        ('json', '[{"/video/two": 3}, {"/article/three": 2}]'),
    ],
)
def test_request_path_counter_output(line_factory, capsys, output, expected):
    """Test the RequestPathCounter command.

    It creates a breakdown of how many times each URL path has been used.
    """
    cmd = commands.RequestPathCounter()
    for path, count in (('/video/two', 3), ('/article/three', 2)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_slow_requests_results(line_factory):
    """Test the SlowRequests command.

    It lists all requests that took more than 1000 milliseconds to respond.
    """
    cmd = commands.SlowRequests()
    assert cmd.raw_results() == []
    for total_time in (1003, 987, 456, 2013, 45000, 1000, 3200, 999):
        cmd(line_factory(tr=total_time))
    results = cmd.raw_results()
    assert results == [1000, 1003, 2013, 3200, 45000]


@pytest.mark.parametrize(
    'output, expected',
    [
        (None, [1000, 1003, 2013, 3200, 45000]),
        ('json', '[1000, 1003, 2013, 3200, 45000]'),
    ],
)
def test_slow_requests_output(line_factory, capsys, output, expected):
    """Test the SlowRequests command.

    It lists all requests that took more than 1000 milliseconds to respond.
    """
    cmd = commands.SlowRequests()
    for total_time in (1003, 987, 456, 2013, 45000, 1000, 3200, 999):
        cmd(line_factory(tr=total_time))
    check_output(cmd, output, expected, capsys)


def test_top_request_paths_results(line_factory):
    """Test the TopRequestPaths command.

    It lists the 10 most used URL paths, and how much where they used.
    """
    cmd = commands.TopRequestPaths()
    assert cmd.raw_results() == []
    for path, count in ((f'/file/{x}', x) for x in range(11)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 10
    assert results[0] == ('/file/10', 10)
    assert results[1] == ('/file/9', 9)
    assert results[2] == ('/file/8', 8)
    assert results[3] == ('/file/7', 7)
    assert results[4] == ('/file/6', 6)
    assert results[5] == ('/file/5', 5)
    assert results[6] == ('/file/4', 4)
    assert results[7] == ('/file/3', 3)
    assert results[8] == ('/file/2', 2)
    assert results[9] == ('/file/1', 1)


def test_top_request_paths_print_results(line_factory):
    """Test the TopRequestPaths command.

    Ensure that when they are printed, only 10 results are shown.
    """
    cmd = commands.TopRequestPaths()
    for path, count in ((f'/file/{x}', x) for x in range(14)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    results = cmd.print_data()
    results = [x for x in results.split('\n') if x]
    assert len(results) == 10
    assert results[0] == '- /file/13: 13'
    assert results[-1] == '- /file/4: 4'


@pytest.mark.parametrize(
    'output, expected',
    [
        (None, '- /file/2: 2\n- /file/1: 1'),
        ('json', '[{"/file/2": 2}, {"/file/1": 1}]'),
    ],
)
def test_top_request_paths_output(line_factory, capsys, output, expected):
    """Test the TopRequestPaths command.

    It lists the 10 most used URL paths, and how much where they used.
    """
    cmd = commands.TopRequestPaths()
    for path, count in ((f'/file/{x}', x) for x in range(3)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_slow_requests_counter_results(line_factory):
    """Test the SlowRequestsCounter command.

    It counts how many requests took more than 1000 milliseconds to complete.
    """
    cmd = commands.SlowRequestsCounter()
    assert cmd.raw_results() == 0
    for total_time in (1003, 987, 456, 2013, 45000, 1000, 3200, 999):
        cmd(line_factory(tr=total_time))
    results = cmd.raw_results()
    assert results == 5


@pytest.mark.parametrize('output', [None, 'json'])
def test_slow_requests_counter_output(line_factory, capsys, output):
    """Test the SlowRequestsCounter command.

    It counts how many requests took more than 1000 milliseconds to complete.
    """
    cmd = commands.SlowRequestsCounter()
    for total_time in (1003, 987, 456, 2013, 45000, 1000, 3200, 999):
        cmd(line_factory(tr=total_time))
    check_output(cmd, output, 5, capsys)


@pytest.mark.parametrize(
    'series, average',
    [
        ((1003, 987, 456, 2013, 1000, 3200, 999), 1379.71),
        ((110, -1, 110), 110),  # aborted connections are ignored
        ((45, 30, 0), 25),  # responses that take 0 milliseconds are still counted
    ],
)
def test_average_response_time_results(line_factory, series, average):
    """Test the AverageResponseTime command.

    Returns the average response time of all valid requests.
    """
    cmd = commands.AverageResponseTime()
    assert cmd.raw_results() == 0.0
    for total_time in series:
        cmd(line_factory(tr=total_time))
    results = cmd.raw_results()
    assert results == average


@pytest.mark.parametrize('output', [None, 'json'])
def test_average_response_time_output(line_factory, capsys, output):
    """Test the AverageResponseTime command.

    Returns the average response time of all valid requests.
    """
    cmd = commands.AverageResponseTime()
    for total_time in (
        40,
        30,
    ):
        cmd(line_factory(tr=total_time))
    check_output(cmd, output, 35.0, capsys)


@pytest.mark.parametrize(
    'series, average',
    [
        ((1003, 987, 456, 2013, 1000, 3200, 999), 1379.71),
        ((110, -1, 110), 110),  # aborted connections are ignored
        ((45, 30, 0), 25),  # requests that do not wait at all are still counted
    ],
)
def test_average_waiting_time_results(line_factory, series, average):
    """Test the AverageWaitingTime command.

    Returns the average time requests had to wait to get processed.
    """
    cmd = commands.AverageWaitingTime()
    assert cmd.raw_results() == 0.0
    for wait_time in series:
        cmd(line_factory(tw=wait_time))
    results = cmd.raw_results()
    assert results == average


@pytest.mark.parametrize('output', [None, 'json'])
def test_average_waiting_time_output(line_factory, capsys, output):
    """Test the AverageWaitingTime command.

    Returns the average time requests had to wait to get processed.
    """
    cmd = commands.AverageWaitingTime()
    for wait_time in (40, 30):
        cmd(line_factory(tw=wait_time))
    check_output(cmd, output, 35.0, capsys)


def test_server_load_results(line_factory):
    """Test the ServerLoad command.

    It creates a breakdown of how many requests each server processed.
    """
    cmd = commands.ServerLoad()
    assert cmd.raw_results() == {}
    for name, count in (('server4', 4), ('server3', 3), ('server5', 5)):
        line = line_factory(server_name=name)
        for _ in range(count):
            cmd(line)
    results = cmd.raw_results()
    assert len(results) == 3
    assert results['server5'] == 5
    assert results['server4'] == 4
    assert results['server3'] == 3


@pytest.mark.parametrize(
    'output, expected',
    [
        (None, '- server5: 5\n- server3: 3'),
        ('json', '[{"server5": 5}, {"server3": 3}]'),
    ],
)
def test_server_load_output(line_factory, capsys, output, expected):
    """Test the ServerLoad command.

    It creates a breakdown of how many requests each server processed.
    """
    cmd = commands.ServerLoad()
    for name, count in (('server3', 3), ('server5', 5)):
        line = line_factory(server_name=name)
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_queue_peaks_no_lines_results(line_factory):
    """Test the QueuePeaks command.

    If there are no log lines processed, nothing should be returned.
    """
    cmd = commands.QueuePeaks()
    assert cmd.raw_results() == []


def test_queue_peaks_no_queues(line_factory):
    """Test the QueuePeaks command.

    If there are no log lines processed, nothing should be returned.
    """
    cmd = commands.QueuePeaks()
    now = datetime.now()
    for second in range(4):
        accept_date = now.replace(second=second).strftime('%d/%b/%Y:%H:%M:%S.%f')
        cmd(line_factory(queue_backend=0, accept_date=accept_date))
    assert len(cmd.requests) == 4
    assert cmd.raw_results() == []


@pytest.mark.parametrize(
    'date,expected_key',
    [
        ('10/Dec/2019:15:40:12.12345', 1575988812.12345),
        ('15/Jan/2017:05:23:05.456', 1484454185.456),
        ('15/Jan/2017:05:23:05.0', 1484454185.0),
    ],
)
def test_queue_peaks_generated_keys(line_factory, date, expected_key):
    """Test the QueuePeaks command.

    Check how the keys for the requests dictionary are generated.
    """
    cmd = commands.QueuePeaks()
    cmd(line_factory(queue_backend=0, accept_date=date))
    keys = list(cmd.requests.keys())
    # account for a 1h difference, if UTC is used (as in CI)
    assert expected_key - 4000 <= keys[0] <= expected_key + 4000
    # check that microseconds are exact though
    assert expected_key - int(expected_key) == keys[0] - int(keys[0])


def test_queue_peaks_details(line_factory):
    """Test the QueuePeaks command.

    Check the information returned for each peak.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([0, 4, 7, 8, 19, 4, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.raw_results()
    assert len(results) == 1
    peak_info = results[0]
    assert peak_info['peak'] == 19
    assert peak_info['span'] == 5
    assert peak_info['started'] == day.replace(microsecond=100000)
    assert peak_info['finished'] == day.replace(microsecond=600000)


def test_queue_peaks_multiple_sorted(line_factory):
    """Test the QueuePeaks command.

    Peaks information are returned sorted by date.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([0, 4, 0, 0, 19, 4, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.raw_results()
    assert len(results) == 2
    assert results[0]['peak'] == 4
    assert results[0]['started'] == day.replace(microsecond=100000)
    assert results[1]['peak'] == 19
    assert results[1]['started'] == day.replace(microsecond=400000)


def test_queue_peaks_already_started(line_factory):
    """Test the QueuePeaks command.

    Check that QueuePeaks handles the corner case of a peak that has already started.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([4, 19, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.raw_results()
    assert len(results) == 1
    peak_info = results[0]
    assert peak_info['peak'] == 19
    assert peak_info['span'] == 2
    assert peak_info['started'] == day
    assert peak_info['finished'] == day.replace(microsecond=200000)


def test_queue_peaks_did_not_finish(line_factory):
    """Test the QueuePeaks command.

    Check that QueuePeaks handles the corner case of a peak that does not finish.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([4, 19, 12]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.raw_results()
    assert len(results) == 1
    peak_info = results[0]
    assert peak_info['peak'] == 19
    assert peak_info['span'] == 3
    assert peak_info['started'] == day
    assert peak_info['finished'] == day.replace(microsecond=200000)


@pytest.mark.parametrize(
    'output, expected',
    [
        (
            None,
            '- peak: 4 - span: 1 - started: 2017-01-15T05:23:05.100000 - finished: 2017-01-15T05:23:05.200000\n'
            '- peak: 19 - span: 2 - started: 2017-01-15T05:23:05.400000 - finished: 2017-01-15T05:23:05.600000',
        ),
        (
            'json',
            '[{"peak": 4, "span": 1, "started": "2017-01-15T05:23:05.100000", "finished": "2017-01-15T05:23:05.200000"}, '
            '{"peak": 19, "span": 2, "started": "2017-01-15T05:23:05.400000", "finished": "2017-01-15T05:23:05.600000"}]',
        ),
    ],
)
def test_queue_peaks_output(line_factory, capsys, output, expected):
    """Test the QueuePeaks command.

    Peaks information are returned sorted by date.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([0, 4, 0, 0, 19, 4, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    check_output(cmd, output, expected, capsys)


def test_connection_type_results(line_factory):
    """Test the ConnectionType command.

    It counts how many requests have been made by SSL, and which ones not.
    """
    cmd = commands.ConnectionType()
    assert cmd.raw_results() == (0, 0)
    for path, count in (('/Virtual:443/something', 4), ('/something', 2)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    assert cmd.raw_results() == (4, 2)


@pytest.mark.parametrize(
    'output, expected',
    [(None, '- https: 4\n- http: 2'), ('json', '[{"https": 4}, {"http": 2}]')],
)
def test_connection_type_output(line_factory, capsys, output, expected):
    """Test the ConnectionType command.

    It counts how many requests have been made by SSL, and which ones not.
    """
    cmd = commands.ConnectionType()
    for path, count in (('/Virtual:443/something', 4), ('/something', 2)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for _ in range(count):
            cmd(line)
    check_output(cmd, output, expected, capsys)


def test_requests_per_minute_results(line_factory):
    """Test the RequestsPerMinute command.

    It counts how many requests have been made per minute.
    """
    cmd = commands.RequestsPerMinute()
    assert cmd.raw_results() == []
    now = datetime.now()
    # to avoid leaping into the next/previous minute with the timedeltas below
    now = now.replace(second=30)
    microseconds = timedelta(microseconds=200)
    seconds = timedelta(seconds=5)
    minutes = timedelta(minutes=5)
    hours = timedelta(hours=2)
    dates = [
        now,
        now + microseconds,
        now - microseconds,
        now + seconds,
        now - seconds,
        now + minutes,
        now - minutes,
        now + hours,
        now - hours,
    ]
    for time in dates:
        cmd(line_factory(accept_date=f'{time:%d/%b/%Y:%H:%M:%S.%f}'))
    results = cmd.raw_results()
    assert len(results) == 5
    assert results[0][1] == 1
    assert results[1][1] == 1
    assert results[2][1] == 5  # now and the +- microseconds and +- seconds
    assert results[3][1] == 1
    assert results[4][1] == 1


@pytest.mark.parametrize('output', [None, 'json'])
def test_requests_per_minute_output(line_factory, capsys, output):
    """Test the RequestsPerMinute command.

    It counts how many requests have been made per minute.
    """
    cmd = commands.RequestsPerMinute()
    now = datetime.now()
    for time in (now, now + timedelta(hours=2)):
        cmd(line_factory(accept_date=f'{time:%d/%b/%Y:%H:%M:%S.%f}'))
    name = cmd.command_line_name().upper()
    cmd.results(output=output)
    output_text = capsys.readouterr().out
    if output == 'json':
        assert f'{{"{name}": ' in output_text
        # this is quite fuzzy to not have to fiddle with the date formatting
        # change it once we hit 2030 :)
        assert ':00": 1}, {"202' in output_text
    else:
        assert f'{name}\n====' in output_text
        # this is quite fuzzy to not have to fiddle with the date formatting
        assert ':00: 1\n- ' in output_text


def test_requests_per_hour_results(line_factory):
    """Test the RequestsPerHour command.

    It counts how many requests have been made per hour.
    """
    cmd = commands.RequestsPerHour()
    assert cmd.raw_results() == []
    specific_date = datetime(year=2022, month=12, day=3, hour=14, minute=10, second=30)
    minutes = timedelta(minutes=5)
    hours = timedelta(hours=2)
    dates = [
        specific_date,
        specific_date + minutes,
        specific_date - minutes,
        specific_date + hours,
        specific_date - hours,
        specific_date + hours * 2,
        specific_date - hours * 2,
    ]
    for time in dates:
        cmd(line_factory(accept_date=f'{time:%d/%b/%Y:%H:%M:%S.%f}'))
    results = cmd.raw_results()
    assert len(results) == 5
    assert results[0][1] == 1
    assert results[1][1] == 1
    assert results[2][1] == 3  # now and the +- minutes
    assert results[3][1] == 1
    assert results[4][1] == 1


@pytest.mark.parametrize('output', [None, 'json'])
def test_requests_per_hour_output(line_factory, capsys, output):
    """Test the RequestsPerHour command.

    It counts how many requests have been made per hour.
    """
    cmd = commands.RequestsPerHour()
    now = datetime.now()
    for time in (now, now + timedelta(hours=2)):
        cmd(line_factory(accept_date=f'{time:%d/%b/%Y:%H:%M:%S.%f}'))
    name = cmd.command_line_name().upper()
    cmd.results(output=output)
    output_text = capsys.readouterr().out
    if output == 'json':
        assert f'{{"{name}": ' in output_text
        # this is quite fuzzy to not have to fiddle with the date formatting
        # change it once we hit 2030 :)
        assert ':00": 1}, {"202' in output_text
    else:
        assert f'{name}\n====' in output_text
        # this is quite fuzzy to not have to fiddle with the date formatting
        assert ':00: 1\n- ' in output_text


def test_print_results_and_output(line_factory, capsys):
    """Test the Print command.

    It simply prints the verbatim line.
    """
    cmd = commands.Print()
    assert cmd.raw_results() is None
    for path in ('/first-thing-to-do', '/second/thing/to-do'):
        cmd(line_factory(http_request=f'GET {path} HTTP/1.1'))
    assert cmd.raw_results() is None
    output_text = capsys.readouterr().out
    lines = output_text.split('\n')
    assert len(lines) == 3
    assert '/first-thing-to-do' in lines[0]
    assert '/second/thing/to-do' in lines[1]
    assert lines[2] == ''
