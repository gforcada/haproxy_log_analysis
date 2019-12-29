from datetime import timedelta
from datetime import datetime
from haproxy.utils import delta_str_to_timedelta
from haproxy.utils import date_str_to_datetime

import pytest


@pytest.mark.parametrize(
    'text, expected',
    [
        ('45s', timedelta(seconds=45)),
        ('2m', timedelta(minutes=2)),
        ('13h', timedelta(hours=13)),
        ('2d', timedelta(days=2)),
    ],
)
def test_str_to_timedelta(text, expected):
    """Check that deltas are converted to timedelta objects."""
    assert delta_str_to_timedelta(text) == expected


@pytest.mark.parametrize(
    'text, expected',
    [
        ('04/Jan/2013', datetime(2013, 1, 4)),
        ('13/May/2015:13', datetime(2015, 5, 13, 13)),
        ('22/Jun/2017:12:11', datetime(2017, 6, 22, 12, 11)),
        ('29/Aug/2019:10:09:08', datetime(2019, 8, 29, 10, 9, 8)),
    ],
)
def test_str_to_datetime(text, expected):
    """Check that start are converted to datetime objects."""
    assert date_str_to_datetime(text) == expected
