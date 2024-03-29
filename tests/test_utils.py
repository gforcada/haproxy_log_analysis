from datetime import datetime
from datetime import timedelta
from haproxy.utils import date_str_to_datetime
from haproxy.utils import delta_str_to_timedelta
from haproxy.utils import VALID_COMMANDS
from haproxy.utils import VALID_FILTERS
from haproxy.utils import validate_arg_date
from haproxy.utils import validate_arg_delta

import pytest


@pytest.mark.parametrize(
    ('text', 'expected'),
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
    ('text', 'expected'),
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


@pytest.mark.parametrize('cmd_key', [*VALID_COMMANDS])
def test_valid_commands(cmd_key):
    """Check that the commands' information is complete."""
    cmd_data = VALID_COMMANDS[cmd_key]
    assert cmd_data['klass']
    assert cmd_data['klass'].command_line_name() == cmd_key
    assert cmd_data['description']
    assert cmd_data['description'].startswith(f'{cmd_key}:\n\t')


@pytest.mark.parametrize('filter_key', [*VALID_FILTERS])
def test_valid_filters(filter_key):
    """Check that the filters' information is complete."""
    filter_data = VALID_FILTERS[filter_key]
    assert filter_data['obj']
    assert filter_data['obj'].__name__ == f'filter_{filter_key}'
    assert filter_data['description']
    assert filter_data['description'].startswith(f'{filter_key}:\n\t')


@pytest.mark.parametrize(('value', 'expected'), [('', None), ('30/Dec/2019', True)])
def test_validate_date(value, expected):
    """Check that the date is validated or an exception raised."""
    if expected is None:
        with pytest.raises(ValueError, match='--start argument is not valid'):
            validate_arg_date(value)
    else:
        assert validate_arg_date(value) is None


@pytest.mark.parametrize(('value', 'expected'), [('', None), ('3d', True)])
def test_validate_delta(value, expected):
    """Check that the delta is validated or an exception raised."""
    if expected is None:
        with pytest.raises(ValueError, match='--delta argument is not valid'):
            validate_arg_delta(value)

    else:
        assert validate_arg_delta(value) is None
