from .exceptions import MissingParameterError, InvalidParameterError


def parse_sea_level(sea_level_param):
    if sea_level_param is None:
        raise MissingParameterError(
            'Missing required query parameter `sea_level`')
    try:
        return float(sea_level_param)
    except ValueError:
        raise InvalidParameterError(
            'Invalid floating point value for `sea_level`: "{}"'.format(
                sea_level_param))
