from nose.tools import assert_equal

from rest_framework.test import APITestCase

from api.apps.tide_gauges.models import TideGauge

_URL = ('/1/tide-gauges/raw-measurements/gladstone/'
        '?start=2014-01-01T00:00:00Z'
        '&end=2014-01-02T00:00:00Z')


class TestRawMeasurementsEndpointMetadata(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.gladstone = TideGauge.objects.create(slug='gladstone')

    @classmethod
    def stearDownClass(cls):
        cls.gladstone.delete()

    def test_that_http_options_allowed_methods_are_get_post_head_options(self):
        response = self.client.options(_URL)
        assert_equal(200, response.status_code)
        assert_equal('GET, POST, HEAD, OPTIONS', response['Allow'])

    def test_that_http_get_is_allowed(self):
        response = self.client.get(_URL)
        assert_equal(200, response.status_code)
