from nose.tools import assert_equal

from rest_framework.test import APITestCase

from api.apps.tide_gauges.models import TideGauge
from api.apps.users.helpers import create_user

_URL = ('/1/tide-gauges/raw-measurements/gladstone/'
        '?start=2014-01-01T00:00:00Z'
        '&end=2014-01-02T00:00:00Z')


class TestRawMeasurementsEndpointMetadata(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.gladstone = TideGauge.objects.create(slug='gladstone')

        cls.normal_user = create_user(
            'user-normal', is_internal_collector=False)

        cls.collector_user = create_user(
            'user-collector', is_internal_collector=True)

    @classmethod
    def tearDownClass(cls):
        cls.gladstone.delete()
        cls.normal_user.delete()
        cls.collector_user.delete()

    def test_that_anonymous_user_cannot_use_http_options(self):
        response = self.client.options(_URL)
        assert_equal(401, response.status_code)

    def test_that_non_collector_user_cannot_use_http_options(self):
        self.client.force_authenticate(self.normal_user)
        response = self.client.options(_URL)
        assert_equal(403, response.status_code)

    def test_that_http_options_allowed_methods_are_get_post_head_options(self):
        self.client.force_authenticate(self.collector_user)
        response = self.client.options(_URL)
        assert_equal(200, response.status_code)
        assert_equal('GET, POST, HEAD, OPTIONS', response['Allow'])
