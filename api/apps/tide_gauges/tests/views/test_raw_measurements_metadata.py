from nose.tools import assert_equal

from rest_framework.test import APITestCase

from api.libs.test_utils import decode_json
from api.apps.tide_gauges.models import TideGauge

_URL = '/1/tide-gauges/raw-measurements/gladstone/'


class TestRawMeasurementsEndpointMetadata(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.gladstone = TideGauge.objects.create(slug='gladstone')

    @classmethod
    def stearDownClass(cls):
        cls.gladstone.delete()

    def test_that_http_options_allowed_methods_are_post_and_options(self):
        response = self.client.options(_URL)
        assert_equal(200, response.status_code)
        assert_equal('POST, OPTIONS', response['Allow'])

    def test_that_http_get_is_not_allowed(self):
        response = self.client.get(_URL)
        assert_equal(405, response.status_code)
        assert_equal(
            {'detail': "Method 'GET' not allowed."},
            decode_json(response.content))
