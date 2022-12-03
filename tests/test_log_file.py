from datetime import datetime

import pytest

from haproxy.logfile import Log


def test_logfile_default_values():
    """Check that the default values are set."""
    log_file = Log('something')
    assert log_file.logfile == 'something'
    assert log_file.show_invalid is False
    assert log_file.invalid_lines == 0
    assert log_file.valid_lines == 0
    assert log_file.total_lines == 0
    assert log_file.start is None
    assert log_file.end is None


@pytest.mark.parametrize(
    'start_str, start_obj, delta, end_obj',
    [
        (None, None, None, None),
        (None, None, '3d', None),
        ('12/Dec/2019', datetime(2019, 12, 12), None, None),
        ('12/Dec/2019', datetime(2019, 12, 12), '3d', datetime(2019, 12, 15)),
    ],
)
def test_start_and_end_attributes(start_str, start_obj, delta, end_obj):
    """Check that the start and end of attributes of Log objects are set as expected."""
    log_file = Log('something', start=start_str, delta=delta)
    assert log_file.logfile == 'something'
    assert log_file.invalid_lines == 0
    assert log_file.start == start_obj
    assert log_file.end == end_obj


@pytest.mark.parametrize('accept_date', ['09/Dec/2013:12:59:46.633', None])
def test_lines_validity(tmp_path, line_factory, accept_date):
    """Check that lines are either counted as valid or invalid."""
    file_path = tmp_path / 'haproxy.log'
    line = ''
    if accept_date:
        line = line_factory(accept_date=accept_date).raw_line
    with open(file_path, 'w') as file_obj:
        file_obj.write(f'{line}\n')
    log_file = Log(file_path)
    _ = list(log_file)

    assert log_file.total_lines == 1
    if accept_date:
        assert log_file.valid_lines == 1
        assert log_file.invalid_lines == 0
    else:
        assert log_file.valid_lines == 0
        assert log_file.invalid_lines == 1


@pytest.mark.parametrize(
    'accept_date, start, delta, is_valid',
    [
        # valid line and no time frame, returned
        ('09/Dec/2013:12:59:46.633', None, None, True),
        # invalid line, not returned
        (None, None, None, False),
        # valid line before time frame, not returned
        ('09/Dec/2013:12:59:46.633', '09/Dec/2014', None, False),
        # valid line after time frame, not returned
        ('09/Dec/2013:12:59:46.633', '08/Dec/2012', '3d', False),
        # valid line within time frame, returned
        ('09/Dec/2013:12:59:46.633', '08/Dec/2013', '3d', True),
    ],
)
def test_returned_lines(tmp_path, line_factory, accept_date, start, delta, is_valid):
    """Check that lines are only returned if they are valid AND within the time frame."""
    file_path = tmp_path / 'haproxy.log'
    line = ''
    if accept_date:
        line = line_factory(accept_date=accept_date).raw_line
    with open(file_path, 'w') as file_obj:
        file_obj.write(f'{line}\n')
    log_file = Log(file_path, start=start, delta=delta)
    lines = list(log_file)
    assert bool(len(lines)) is is_valid


def test_total_lines():
    """Check that the total amount of lines are always counted."""
    log_file = Log(logfile='tests/files/2_ok_1_invalid.log')
    _ = list(log_file)
    assert log_file.total_lines == 3
    assert log_file.valid_lines == 2
    assert log_file.invalid_lines == 1


@pytest.mark.parametrize('headers', [' {1.2.3.4}', 'random-value-that-breaks'])
def test_print_invalid_lines(tmp_path, line_factory, headers, capsys):
    """Check that invalid lines are printed, if asked to do so."""
    file_path = tmp_path / 'haproxy.log'
    line = line_factory(headers=headers).raw_line
    with open(file_path, 'w') as file_obj:
        file_obj.write(f'{line}\n')
    log_file = Log(file_path, show_invalid=True)
    _ = list(log_file)

    output = capsys.readouterr().out
    if log_file.valid_lines == 1:
        assert headers not in output
    else:
        assert headers in output
