def filter_ip(ip):
    """Filter by IP.

    -f ip[192.168.1.2]  # will return only lines that have this IP.

    Either the client IP, or, if present, the first IP captured
    in the X-Forwarded-For header.
    """

    def filter_func(log_line):
        return log_line.ip == ip

    return filter_func


def filter_ip_range(ip_range):
    """Filter by an IP range.

    -f ip_range[192.168.1]

    Rather than proper IP ranges, is a string matching.
    See `ip` filter about which IP is being.
    """

    def filter_func(log_line):
        ip = log_line.ip
        if ip:
            return ip.startswith(ip_range)

    return filter_func


def filter_path(path):
    """Filter by the request path.

    -f path[/one/two]

    It looks for the given path to be part of the requested path.
    """

    def filter_func(log_line):
        return path in log_line.http_request_path

    return filter_func


def filter_ssl(ignore=True):
    """Filter by SSL connection.

    -f ssl

    It checks that the request is made via the standard https port.
    """

    def filter_func(log_line):
        return log_line.is_https

    return filter_func


def filter_slow_requests(slowness):
    """Filter by response time.

    -f slow_requests[1000]  # get all lines that took more than a second to process

    Filters by the time it took the downstream server to process the request.
    Time is in milliseconds.
    """

    def filter_func(log_line):
        slowness_int = int(slowness)
        return slowness_int <= log_line.time_wait_response

    return filter_func


def filter_wait_on_queues(max_waiting):
    """Filter by queue time in HAProxy.

    -f wait_on_queues[1000]  # get all requests that waited more than a second in HAProxy

    Filters by the time a request had to wait in HAProxy
    prior to be sent to a downstream server to be processed.
    """

    def filter_func(log_line):
        waiting = int(max_waiting)
        return waiting <= log_line.time_wait_queues

    return filter_func


def filter_status_code(http_status):
    """Filter by a specific HTTP status code.

    -f status_code[404]
    """

    def filter_func(log_line):
        return log_line.status_code == http_status

    return filter_func


def filter_status_code_family(family_number):
    """Filter by a family of HTTP status code.

    -f status_code_family[5]  # get all 5xx status codes
    """

    def filter_func(log_line):
        return log_line.status_code.startswith(family_number)

    return filter_func


def filter_http_method(http_method):
    """Filter by HTTP method (GET, POST, PUT, HEAD...).

    -f http_method[GET]
    """

    def filter_func(log_line):
        return log_line.http_request_method == http_method

    return filter_func


def filter_backend(backend_name):
    """Filter by HAProxy backend.

    -f backend[specific_app]

    See HAProxy configuration, it can have multiple backends defined.
    """

    def filter_func(log_line):
        return log_line.backend_name == backend_name

    return filter_func


def filter_frontend(frontend_name):
    """Filter by which HAProxy frontend got the request.

    -f frontend[loadbalancer]

    See HAProxy configuration, it can have multiple frontends defined.
    """

    def filter_func(log_line):
        return log_line.frontend_name == frontend_name

    return filter_func


def filter_server(server_name):
    """Filter by downstream server.

    -f server[app01]
    """

    def filter_func(log_line):
        return log_line.server_name == server_name

    return filter_func


def filter_response_size(size):
    """Filter by how big (in bytes) the response was.

    -f response_size[50000]

    Specially useful when looking for big file downloads.
    """
    if size.startswith('+'):
        size_value = int(size[1:])
    else:
        size_value = int(size)

    def filter_func(log_line):
        bytes_read = log_line.bytes_read
        if bytes_read.startswith('+'):
            bytes_read = int(bytes_read[1:])
        else:
            bytes_read = int(bytes_read)

        return bytes_read >= size_value

    return filter_func
