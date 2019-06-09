# -*- coding: utf-8 -*-
import re


__import__('pkg_resources').declare_namespace(__name__)


DELTA_REGEX = re.compile(r'\A(?P<value>\d+)(?P<time_unit>[smhd])\Z')

START_REGEX = re.compile(
    r'(?P<day>\d+)/(?P<month>\w+)/(?P<year>\d+)'
    r'(:(?P<hour>\d+)|)(:(?P<minute>\d+)|)(:(?P<second>\d+)|)'
)
