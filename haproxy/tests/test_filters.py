import pytest

from haproxy import filters


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('1.2.3.4', '1.2.3.4', True),
        ('2.3.4.5', '5.3.5.4', False),
        ('2001:db8::8a2e:370:7334', '2001:db8::8a2e:370:7334', True),
        ('2001:db8::8a2e:370:7334', '2001:db8::8a2e:456:7321', False),
    ],
)
def test_filter_ip(line_factory, to_filter, to_check, result):
    """Check that filter_ip filter works as expected."""
    current_filter = filters.filter_ip(to_filter)
    headers = f' {{{to_check}}}'
    line = line_factory(headers=headers)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('1.2.3', '1.2.3.4', True),
        ('1.2.3', '1.2.3.78', True),
        ('2.3.4.5', '5.3.5.4', False),
        ('2001:db8', '2001:db8::8a2e:370:7334', True),
        ('2001:db8', '2001:db8::8a2e:456:7321', True),
        ('2134:db8', '2001:db8::8a2e:456:7321', False),
    ],
)
def test_filter_ip_range(line_factory, to_filter, to_check, result):
    """Check that filter_ip_range filter works as expected."""
    current_filter = filters.filter_ip_range(to_filter)
    headers = f' {{{to_check}}}'
    line = line_factory(headers=headers)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'path, result',
    [
        ('/path/to/image', True),
        ('/something/else', False),
        ('/another/image/here', True),
    ],
)
def test_filter_path(line_factory, path, result):
    """Check that filter_path filter works as expected."""
    current_filter = filters.filter_path('/image')
    http_request = f'GET {path} HTTP/1.1'
    line = line_factory(http_request=http_request)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'path, result',
    [
        ('/ssl_path:443/image', True),
        ('/something/else', False),
        ('/another:443/ssl', True),
    ],
)
def test_filter_ssl(line_factory, path, result):
    """Check that filter_path filter works as expected."""
    current_filter = filters.filter_ssl()
    http_request = f'GET {path} HTTP/1.1'
    line = line_factory(http_request=http_request)
    assert current_filter(line) is result


@pytest.mark.parametrize('tr, result', [(45, False), (13000, True), (4566, False)])
def test_filter_slow_requests(line_factory, tr, result):
    """Check that filter_slow_requests filter works as expected."""
    current_filter = filters.filter_slow_requests('10000')
    line = line_factory(tr=tr)
    assert current_filter(line) is result


@pytest.mark.parametrize('tw, result', [(45, True), (13000, False), (4566, False)])
def test_filter_wait_on_queues(line_factory, tw, result):
    """Check that filter_wait_on_queues filter works as expected"""
    current_filter = filters.filter_wait_on_queues('50')
    line = line_factory(tw=tw)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('200', '200', True),
        ('200', '230', False),
        ('300', '300', True),
        ('300', '400', False),
    ],
)
def test_filter_status_code(line_factory, to_filter, to_check, result):
    """Test that the status_code filter works as expected."""
    current_filter = filters.filter_status_code(to_filter)
    line = line_factory(status=to_check)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('2', '200', True),
        ('2', '230', True),
        ('2', '300', False),
        ('3', '300', True),
        ('3', '330', True),
        ('3', '400', False),
    ],
)
def test_filter_status_code_family(line_factory, to_filter, to_check, result):
    """Test that the status_code_family filter works as expected."""
    current_filter = filters.filter_status_code_family(to_filter)
    line = line_factory(status=to_check)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('GET', 'GET', True),
        ('GET', 'POST', False),
        ('GET', 'PUT', False),
        ('GET', 'PATCH', False),
        ('GET', 'DELETE', False),
        ('PATCH', 'PATCH', True),
        ('DELETE', 'DELETE', True),
    ],
)
def test_filter_http_method(line_factory, to_filter, to_check, result):
    """Test that the http_method filter works as expected."""
    current_filter = filters.filter_http_method(to_filter)
    line = line_factory(http_request=f'{to_check} /path HTTP/1.1')
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('default', 'default', True),
        ('default', 'backend', False),
        ('backend', 'backend', True),
        ('backend', 'default', False),
    ],
)
def test_filter_backend(line_factory, to_filter, to_check, result):
    """Test that the backend filter works as expected."""
    current_filter = filters.filter_backend(to_filter)
    line = line_factory(backend_name=to_check)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('varnish', 'varnish', True),
        ('varnish', 'nginx', False),
        ('nginx', 'nginx', True),
        ('nginx', 'varnish', False),
    ],
)
def test_filter_frontend(line_factory, to_filter, to_check, result):
    """Test that the frontend filter works as expected."""
    current_filter = filters.filter_frontend(to_filter)
    line = line_factory(frontend_name=to_check)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('server1', 'server1', True),
        ('server1', 'backend23', False),
        ('backend23', 'backend23', True),
        ('backend23', 'server1', False),
    ],
)
def test_filter_server(line_factory, to_filter, to_check, result):
    """Test that the server filter works as expected."""
    current_filter = filters.filter_server(to_filter)
    line = line_factory(server_name=to_check)
    assert current_filter(line) is result


@pytest.mark.parametrize(
    'to_filter, to_check, result',
    [
        ('400', '500', True),
        ('400', '+500', True),
        ('+400', '500', True),
        ('+400', '+500', True),
        ('400', '300', False),
        ('400', '+300', False),
        ('+400', '300', False),
        ('+400', '+300', False),
    ],
)
def test_filter_response_size(line_factory, to_filter, to_check, result):
    """Test that the size filter works as expected.

    Note that both filter and value can have a leading plus sign.
    """
    current_filter = filters.filter_response_size(to_filter)
    line = line_factory(bytes=to_check)
    assert current_filter(line) is result
