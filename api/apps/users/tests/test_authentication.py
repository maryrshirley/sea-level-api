from django.test import TestCase

from nose_parameterized import parameterized
from nose.tools import assert_equal


_URL_AUTH = '/1/authenticate'
_URL_VALIDATE = '/1/authenticate/validate'


def load_endpoint_test_cases():
    cases = [(_URL_AUTH, 'POST, OPTIONS',),
             (_URL_VALIDATE, 'POST, OPTIONS',)]

    return cases


class TestAuthentication(TestCase):

    @parameterized.expand(load_endpoint_test_cases)
    def test_that_http_options_allowed(self, url, allow):
        response = self.client.options(url)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])
