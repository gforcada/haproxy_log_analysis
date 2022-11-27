from copy import deepcopy

import pytest

from haproxy.line import Line

DEFAULT_DATA = {
    'syslog_date': 'Dec  9 13:01:26',
    'process_name_and_pid': 'localhost haproxy[28029]:',
    'client_ip': '127.0.0.1',
    'client_port': 2345,
    'accept_date': '09/Dec/2013:12:59:46.633',
    'frontend_name': 'loadbalancer',
    'backend_name': 'default',
    'server_name': 'instance8',
    'tq': 0,
    'tw': 51536,
    'tc': 1,
    'tr': 48082,
    'tt': '99627',
    'status': '200',
    'bytes': '83285',
    'act': '87',
    'fe': '89',
    'be': '98',
    'srv': '1',
    'retries': '20',
    'queue_server': 2,
    'queue_backend': 67,
    'headers': ' {77.24.148.74}',
    'http_request': 'GET /path/to/image HTTP/1.1',
}


class LinesGenerator:
    def __init__(self, line_format):
        self.data = deepcopy(DEFAULT_DATA)
        self.line_format = line_format

    def __call__(self, *args, **kwargs):
        self.data.update(**kwargs)
        self.data['client_ip_and_port'] = '{client_ip}:{client_port}'.format(
            **self.data
        )
        self.data[
            'server_names'
        ] = '{frontend_name} {backend_name}/{server_name}'.format(**self.data)
        self.data['timers'] = '{tq}/{tw}/{tc}/{tr}/{tt}'.format(**self.data)
        self.data['status_and_bytes'] = '{status} {bytes}'.format(**self.data)
        self.data['connections_and_retries'] = '{act}/{fe}/{be}/{srv}/{retries}'.format(
            **self.data
        )
        self.data['queues'] = '{queue_server}/{queue_backend}'.format(**self.data)

        log_line = self.line_format.format(**self.data)
        return Line(log_line)


@pytest.fixture
def default_line_data():
    return DEFAULT_DATA


@pytest.fixture
def line_factory():
    # queues and headers parameters are together because if no headers are
    # saved the field is completely empty and thus there is no double space
    # between queue backend and http request.
    raw_line = (
        '{syslog_date} {process_name_and_pid} {client_ip_and_port} '
        '[{accept_date}] {server_names} {timers} {status_and_bytes} '
        '- - ---- {connections_and_retries} {queues}{headers} '
        '"{http_request}"'
    )
    generator = LinesGenerator(raw_line)
    return generator
