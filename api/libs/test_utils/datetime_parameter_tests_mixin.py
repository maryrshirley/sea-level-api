from .assert_json_response import assert_json_response


class DatetimeParameterTestsMixin(object):
    """
    Provides tests for a URL endpoint to validate against our DATETIME_FORMAT
    which looks like `YYYY-MM-DDTHH:MM:00Z'

    Inherit from APITestCase and this Mixin and set a class fields eg:

    TEST_PATH='/my/path/?start_datetime={test_datetime}'

    Then this test will run substitute the `test_datetime` parameter, testing
    for HTTP 400  with good error messages.
    """

    def _path(self, datetime_string):
        # return urllib.parse.quote(
        return self.TEST_PATH.format(test_datetime=datetime_string)

    def _get(self, datetime_string):
        return self.client.get(self._path(datetime_string))

    def test_that_localtime_datetime_has_400_json_error(self):
        expected_json = {'detail': 'Invalid datetime `2016-01-01T10:25:00`. '
                                   'Expected format: %Y-%m-%dT%H:%M:00Z'}
        assert_json_response(
            self._get('2016-01-01T10:25:00'), 400, expected_json)

    def test_that_hour_offset_utc_format_datetime_has_400_json_error(self):
        expected_json = {'detail': 'Invalid datetime '
                                   '`2016-01-01T10:25:00+06:00`. '
                                   'Expected format: %Y-%m-%dT%H:%M:00Z'}
        assert_json_response(
            self._get('2016-01-01T10:25:00' '%2B' '06:00'), 400, expected_json)

    def test_that_microseconds_in_datetime_has_400_json_error(self):
        expected_json = {'detail': 'Invalid datetime '
                                   '`2016-01-01T10:25:00.123Z`. '
                                   'Expected format: %Y-%m-%dT%H:%M:00Z'}
        assert_json_response(
            self._get('2016-01-01T10:25:00.123Z'), 400, expected_json)

    def test_that_non_zero_seconds_in_datetime_has_400_json_error(self):
        expected_json = {'detail': 'Invalid datetime `2016-01-01T10:25:01Z`. '
                                   'Expected format: %Y-%m-%dT%H:%M:00Z'}
        assert_json_response(
            self._get('2016-01-01T10:25:01Z'), 400, expected_json)
