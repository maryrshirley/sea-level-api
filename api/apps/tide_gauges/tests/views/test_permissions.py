from rest_framework.test import APITestCase
from nose.tools import assert_equal

from api.libs.user_permissions.tests.create_test_users_locations import (
    create_test_users_locations,)

from api.apps.tide_gauges.models import TideGauge


class TestRawMeasurementsPermissions(APITestCase):

    @classmethod
    def setUpClass(cls):
        cls.tide_gauage = TideGauge.objects.create(
            slug='tide-gauge-1', comment='Tide Gauge 1')

        cls.test_users_locations = create_test_users_locations()

    @classmethod
    def tearDownClass(cls):
        cls.tide_gauage.delete()

        for obj in cls.test_users_locations.values():
            obj.delete()

    READ_URL = (
        '/1/tide-gauges/raw-measurements/tide-gauge-1/'
        '?start=2014-11-30T00:00:00Z&end=2014-11-30T00:00:00Z'
    )

    WRITE_URL = '/1/tide-gauges/raw-measurements/tide-gauge-1/'

    def assert_status(self, expected_status, method, user):
        if user is not None:
            self.client.force_authenticate(self.test_users_locations[user])

        if method == 'GET':
            response = self.client.get(self.READ_URL)

        elif method == 'POST':
            response = self.client.post(
                self.WRITE_URL, data='[]', content_type='application/json')

        else:
            raise ValueError(method)

        assert_equal(expected_status, response.status_code)

    def test_that_anonymous_users_cannot_GET_raw_measurements(self):
        self.assert_status(401, 'GET', None)

    def test_that_anonymous_users_cannot_POST_raw_measurements(self):
        self.assert_status(401, 'POST', None)

    def test_that_logged_in_users_cannot_GET_raw_measurements(self):
        self.assert_status(403, 'GET', 'user-1')

    def test_that_logged_in_users_cannot_POST_raw_measurements(self):
        self.assert_status(403, 'POST', 'user-1')

    def test_that_collectors_can_GET_raw_measurements(self):
        self.assert_status(200, 'GET', 'user-collector')

    def test_that_collectors_can_POST_raw_measurements(self):
        self.assert_status(201, 'POST', 'user-collector')
