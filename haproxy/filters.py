# -*- coding: utf-8 -*-


def filter_ip(ip):
    """Filter :class:`.HaproxyLogLine` objects by IP.

    :param ip: IP that you want to filter to.
    :type ip: string
    :returns: a function that filters by the provided IP.
    :rtype: function
    """
    def filter_func(log_line):
        return log_line.get_ip() == ip

    return filter_func


def filter_ip_range(ip_range):
    """Filter :class:`.HaproxyLogLine` objects by IP range.

    Both *192.168.1.203* and *192.168.1.10* are valid if the provided ip
    range is ``192.168.1`` whereas *192.168.2.103* is not valid (note the
    *.2.*).

    :param ip: IP range that you want to filter to.
    :type ip: string
    :returns: a function that filters by the provided IP range.
    :rtype: function
    """
    def filter_func(log_line):
        ip = log_line.get_ip()
        if ip:
            return ip.startswith(ip_range)

    return filter_func


def filter_path(path):
    """Filter :class:`.HaproxyLogLine` objects by their request path.

    :param path: part of a path that needs to be on the request path.
    :type path: string
    :returns: a function that filters by the provided path.
    :rtype: function
    """
    def filter_func(log_line):
        return path in log_line.http_request_path

    return filter_func


def filter_ssl():
    """Filter :class:`.HaproxyLogLine` objects that from SSL connections.

    :returns: a function that filters SSL log lines.
    :rtype: function
    """
    def filter_func(log_line):
        return log_line.is_https()

    return filter_func
