def filter_ip(ip):
    """Filter :class:`.Line` objects by IP.

    :param ip: IP that you want to filter to.
    :type ip: string
    :returns: a function that filters by the provided IP.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.ip == ip

    return filter_func


def filter_ip_range(ip_range):
    """Filter :class:`.Line` objects by IP range.

    Both *192.168.1.203* and *192.168.1.10* are valid if the provided ip
    range is ``192.168.1`` whereas *192.168.2.103* is not valid (note the
    *.2.*).

    :param ip_range: IP range that you want to filter to.
    :type ip_range: string
    :returns: a function that filters by the provided IP range.
    :rtype: function
    """

    def filter_func(log_line):
        ip = log_line.ip
        if ip:
            return ip.startswith(ip_range)

    return filter_func


def filter_path(path):
    """Filter :class:`.Line` objects by their request path.

    :param path: part of a path that needs to be on the request path.
    :type path: string
    :returns: a function that filters by the provided path.
    :rtype: function
    """

    def filter_func(log_line):
        return path in log_line.http_request_path

    return filter_func


def filter_ssl(ignore=True):
    """Filter :class:`.Line` objects that from SSL connections.

    :param ignore: parameter to be ignored just to conform to the rule that all
      filters need a parameter
    :type ignore: bool
    :returns: a function that filters SSL log lines.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.is_https

    return filter_func


def filter_slow_requests(slowness):
    """Filter :class:`.Line` objects by their response time.

    :param slowness: minimum time, in milliseconds, a server needs to answer
      a request. If the server takes more time than that the log line is
      accepted.
    :type slowness: string
    :returns: a function that filters by the server response time.
    :rtype: function
    """

    def filter_func(log_line):
        slowness_int = int(slowness)
        return slowness_int <= log_line.time_wait_response

    return filter_func


def filter_wait_on_queues(max_waiting):
    """Filter :class:`.Line` objects by their queueing time in
    HAProxy.

    :param max_waiting: maximum time, in milliseconds, a request is waiting on
      HAProxy prior to be delivered to a backend server. If HAProxy takes less
      than that time the log line is counted.
    :type max_waiting: string
    :returns: a function that filters by HAProxy queueing time.
    :rtype: function
    """

    def filter_func(log_line):
        waiting = int(max_waiting)
        return waiting >= log_line.time_wait_queues

    return filter_func


def filter_status_code(http_status):
    """Filter :class:`.Line` objects by their HTTP status code.

    :param http_status: HTTP status code (200, 404, 502...) to filter lines
      with.
    :type http_status: string
    :returns: a function that filters by HTTP status code.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.status_code == http_status

    return filter_func


def filter_status_code_family(family_number):
    """Filter :class:`.Line` objects by their family of HTTP status
    code, i.e. 2xx, 3xx, 4xx

    :param family_number: First digit of the HTTP status code family, i.e. 2
      to get all the 2xx status codes, 4 for the client errors and so on.
    :type family_number: string
    :returns: a function that filters by HTTP status code family.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.status_code.startswith(family_number)

    return filter_func


def filter_http_method(http_method):
    """Filter :class:`.Line` objects by their HTTP method used (i.e.
    GET, POST...).

    :param http_method: HTTP method (POST, GET...).
    :type http_method: string
    :returns: a function that filters by the given HTTP method.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.http_request_method == http_method

    return filter_func


def filter_backend(backend_name):
    """Filter :class:`.Line` objects by the HAProxy backend name
    they were processed with.

    :param backend_name: Name of the HAProxy backend section to investigate.
    :type backend_name: string
    :returns: a function that filters by the given backend name.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.backend_name == backend_name

    return filter_func


def filter_frontend(frontend_name):
    """Filter :class:`.Line` objects by the HAProxy frontend name
    the connection arrived from.

    :param frontend_name: Name of the HAProxy frontend section to investigate.
    :type frontend_name: string
    :returns: a function that filters by the given frontend name.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.frontend_name == frontend_name

    return filter_func


def filter_server(server_name):
    """Filter :class:`.Line` objects by the downstream server that
    handled the connection.

    :param server_name: Name of the server HAProxy send the connection to.
    :type server_name: string
    :returns: a function that filters by the given server name.
    :rtype: function
    """

    def filter_func(log_line):
        return log_line.server_name == server_name

    return filter_func


def filter_response_size(size):
    """Filter :class:`.Line` objects by the response size (in bytes).

    Specially useful when looking for big file downloads.

    :param size: Minimum amount of bytes a response body weighted.
    :type size: string
    :returns: a function that filters by the response size.
    :rtype: function
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
