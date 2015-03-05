import datetime

from collections import namedtuple

import pytz

from django.conf import settings

from .exceptions import (InvalidDatetimeError, NoStartTimeGivenError,
                         NoEndTimeGivenError)

TimeRange = namedtuple('TimeRange', 'start,end')


def parse_time_range(start, end):
    if start is None:
        raise NoStartTimeGivenError()

    if end is None:
        raise NoEndTimeGivenError()

    return TimeRange(start=parse_datetime(start), end=parse_datetime(end))


def parse_datetime(datetime_string):
    try:
        return datetime.datetime.strptime(
            datetime_string, settings.DATETIME_FORMAT).replace(tzinfo=pytz.UTC)
    except ValueError:
        raise InvalidDatetimeError(
            'Invalid datetime `{}`. Expected format: {}'.format(
                datetime_string, settings.DATETIME_FORMAT))
