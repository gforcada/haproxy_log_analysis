from collections import defaultdict
from collections import OrderedDict

import time


class BaseCommandMixin:
    @classmethod
    def command_line_name(cls):
        """Convert class name to lowercase with underscores.

        i.e. turn HttpMethods to http_methods.
        """
        final_string = cls.__name__[0].lower()
        for character in cls.__name__[1:]:
            if character.isupper():
                final_string += f'_{character.lower()}'
            else:
                final_string += character
        return final_string


class AttributeCounterMixin:

    attribute_name = None

    def __init__(self):
        self.stats = defaultdict(int)

    def __call__(self, line):
        self.stats[getattr(line, self.attribute_name)] += 1

    def results(self):
        return self.stats


class SortTrimMixin:
    @staticmethod
    def _sort_and_trim(data, reverse=False):
        """Sorts a dictionary with at least two fields on each of them sorting
        by the second element.

        .. warning::
          Right now is hardcoded to 10 elements, improve the command line
          interface to allow to send parameters to each command or globally.
        """
        threshold = 10
        data_list = data.items()
        data_list = sorted(
            data_list, key=lambda data_info: data_info[1], reverse=reverse
        )
        return data_list[:threshold]


class Counter(BaseCommandMixin):
    """Count valid lines."""

    def __init__(self):
        self.counter = 0

    def __call__(self, line):
        self.counter += 1

    def results(self):
        return self.counter


class HttpMethods(BaseCommandMixin, AttributeCounterMixin):
    """Report a breakdown of how many requests have been made per HTTP method.

    That is, how many GET, POST, etc requests.
    """

    attribute_name = 'http_request_method'


class IpCounter(BaseCommandMixin, AttributeCounterMixin):
    """Report a breakdown of how many requests have been made per IP."""

    attribute_name = 'ip'


class TopIps(IpCounter, SortTrimMixin):
    """Return the top most frequent IPs.

    .. note::
      See `_sort_and_trim` for its current
      limitations.
    """

    def results(self):
        return self._sort_and_trim(self.stats, reverse=True)


class StatusCodesCounter(BaseCommandMixin, AttributeCounterMixin):
    """Generate statistics about HTTP status codes. 404, 500 and so on."""

    attribute_name = 'status_code'


class RequestPathCounter(BaseCommandMixin, AttributeCounterMixin):
    """Generate statistics about HTTP requests' path."""

    attribute_name = 'http_request_path'


class TopRequestPaths(RequestPathCounter, SortTrimMixin):
    """Returns the top most frequent paths.

    .. note::
      See `_sort_and_trim` for its current
      limitations.
    """

    def results(self):
        return self._sort_and_trim(self.stats, reverse=True)


class SlowRequests(BaseCommandMixin):
    """List all requests that took a certain amount of time to be
    processed.

    .. warning::
       By now hardcoded to 1 second (1000 milliseconds), improve the
       command line interface to allow to send parameters to each command
       or globally.
    """

    threshold = 1000

    def __init__(self):
        self.slow_requests = []

    def __call__(self, line):
        response_time = line.time_wait_response
        if response_time >= self.threshold:
            self.slow_requests.append(response_time)

    def results(self):
        return sorted(self.slow_requests)


class SlowRequestsCounter(SlowRequests):
    """Counts all requests that took a certain amount of time to be
    processed.

    .. warning::
       By now hardcoded to 1 second (1000 milliseconds), improve the
       command line interface to allow to send parameters to each command
       or globally.
    """

    def results(self):
        return len(self.slow_requests)


class AverageResponseTime(SlowRequests):
    """Return the average response time of all valid requests."""

    threshold = 0

    def results(self):
        total_requests = float(len(self.slow_requests))
        if total_requests > 0:
            average = sum(self.slow_requests) / total_requests
            return round(average, 2)
        return 0.0


class AverageWaitingTime(BaseCommandMixin):
    """Return the average response time of all valid requests."""

    def __init__(self):
        self.waiting_times = []

    def __call__(self, line):
        waiting_time = line.time_wait_queues
        if waiting_time >= 0:
            self.waiting_times.append(waiting_time)

    def results(self):
        total_requests = float(len(self.waiting_times))
        if total_requests > 0:
            average = sum(self.waiting_times) / total_requests
            return round(average, 2)
        return 0.0


class ServerLoad(BaseCommandMixin, AttributeCounterMixin):
    """Generate statistics regarding how many requests were processed by
    each downstream server.
    """

    attribute_name = 'server_name'


class QueuePeaks(BaseCommandMixin):
    """Generate a list of the requests peaks on the queue.

    When servers can not handle all incoming requests,
    they have to wait on HAProxy.
    On every log line there is an account for how many requests have been piled up.

    A queue peak is defined by the biggest value on the backend queue
    on a series of log lines that are between log lines with the queue empty.

    .. warning::
      Allow to configure up to which peak can be ignored. Currently
      set to 1.
    """

    def __init__(self):
        self.requests = {}
        self.threshold = 1

    @staticmethod
    def _generate_key(date):
        """Create a suitable unique key out of a python datetime.datetime object."""
        # get the unix timestamp out of the date,
        # after removing the microseconds from it
        no_microseconds = date.replace(microsecond=0)
        time_parts = no_microseconds.timetuple()
        unixtime = time.mktime(time_parts)

        # add back the microseconds to the key, as decimals
        microseconds = date.microsecond / (10 ** len(str(date.microsecond)))
        key = unixtime + microseconds
        return key

    def __call__(self, line):
        key = self._generate_key(line.accept_date)
        self.requests[key] = (line.queue_backend, line.accept_date)

    def results(self):
        sorted_requests = OrderedDict(sorted(self.requests.items()))
        peaks = []
        current_peak = 0
        requests_on_queue = 0
        timestamp = None

        current_span = 0
        first_with_queue = None

        for requests_on_queue, timestamp in sorted_requests.values():
            # set the peak
            if requests_on_queue > current_peak:
                current_peak = requests_on_queue

            # set the span
            if requests_on_queue > 0:
                current_span += 1

                # set when the queue starts
                if first_with_queue is None:
                    first_with_queue = timestamp

            # if the queue is already flushed, record it and reset values
            if requests_on_queue == 0 and current_peak > self.threshold:
                data = {
                    'peak': current_peak,
                    'span': current_span,
                    'first': first_with_queue,
                    'last': timestamp,
                }
                peaks.append(data)
                current_peak = 0
                current_span = 0
                first_with_queue = None

        # case of a series that does not end
        if requests_on_queue > 0 and current_peak > self.threshold:
            data = {
                'peak': current_peak,
                'span': current_span,
                'first': first_with_queue,
                'last': timestamp,
            }
            peaks.append(data)

        return peaks


class ConnectionType(BaseCommandMixin):
    """Generate statistics on how many requests are made via HTTP and how
    many are made via SSL.

    .. note::
      This only works if the request path contains the default port for
      SSL (443).

    .. warning::
      The ports are hardcoded, they should be configurable.
    """

    def __init__(self):
        self.https = 0
        self.non_https = 0

    def __call__(self, line):
        if line.is_https:
            self.https += 1
        else:
            self.non_https += 1

    def results(self):
        return self.https, self.non_https


class RequestsPerMinute(BaseCommandMixin):
    """Generates statistics on how many requests were made per minute.

    .. note::
      Try to combine it with time constrains (``-s`` and ``-d``) as this
      command output can be huge otherwise.
    """

    def __init__(self):
        self.requests = defaultdict(int)

    def __call__(self, line):
        date_with_minute_precision = line.accept_date.replace(second=0, microsecond=0)
        unixtime = time.mktime(date_with_minute_precision.timetuple())
        self.requests[unixtime] += 1

    def results(self):
        """Return the list of requests sorted by the timestamp."""
        data = sorted(self.requests.items(), key=lambda data_info: data_info[0])
        return data


class Print(BaseCommandMixin):
    """Returns the raw lines to be printed."""

    def __call__(self, line):
        print(line.raw_line)

    def results(self):
        return
