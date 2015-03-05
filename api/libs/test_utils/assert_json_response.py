from nose.tools import assert_equal
from .decode_json import decode_json


def assert_json_response(response, expected_status, expected_json):
    assert_equal(expected_status, response.status_code)
    try:
        decoded = decode_json(response.content)
    except ValueError:
        raise AssertionError('Response was not valid JSON: {}'.format(
            response.content))

    assert_equal(expected_json, decoded)
