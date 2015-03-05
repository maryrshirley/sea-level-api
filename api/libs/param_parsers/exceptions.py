from django.conf import settings
from rest_framework.exceptions import APIException


class MissingParameterError(APIException):
    status_code = 400
    default_detail = 'Missing query parameter in URL.'


class InvalidParameterError(APIException):
    status_code = 400
    default_detail = 'Invalid value for query parameter'


class NoStartTimeGivenError(MissingParameterError):
    default_detail = 'Missing parameter `start`. Format: 2014-11-30T00:00:00Z'


class NoEndTimeGivenError(MissingParameterError):
    default_detail = 'Missing parameter `end`. Format: 2014-11-30T00:00:00Z'


class TimeRangeError(InvalidParameterError):
    pass


class InvalidDatetimeError(InvalidParameterError):
    default_detail = 'Invalid datetime. Expected format: {}'.format(
        settings.DATETIME_FORMAT)


class ObjectNotFoundError(InvalidParameterError):
    status_code = 404


class InvalidLocationError(ObjectNotFoundError):
    default_detail = 'Invalid location specified. See the locations endpoint.'
