from nose.tools import assert_equal

from rest_framework.test import APITestCase

from api.libs.minute_in_time.models import Minute
from api.libs.param_parsers.parse_time import parse_datetime


class Mixin(object):
    API_URL = '/1/'

    @property
    def Minute(self):
        return Minute

    def endpoint_url(self, endpoint):
        if not self.live_server_url:
            return None

        return self.live_server_url + endpoint

    def payload_minute_datetime(self, payload):
        payload['minute'], _ = Minute.objects.get_or_create(
            datetime=parse_datetime(payload['minute__datetime']))
        del payload['minute__datetime']
        return payload


class APIUnitTestCase(APITestCase):

    def assert_endpoint_OPTIONS_allowed(self, url, allow):
        response = self.client.options(url)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])
