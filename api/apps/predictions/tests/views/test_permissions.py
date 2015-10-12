from rest_framework.test import APITestCase
from nose.tools import assert_equal

from api.libs.user_permissions.tests.create_test_users_locations import (
    create_test_users_locations,)

TEST_USERS_LOCATIONS = None


def setUpModule():
    global TEST_USERS_LOCATIONS
    TEST_USERS_LOCATIONS = create_test_users_locations()


def tearDownModule():
    global TEST_USERS_LOCATIONS
    for obj in TEST_USERS_LOCATIONS.values():
        obj.delete()


class TestPermissionsMixin(object):
    def assert_status(self, expected_status, location_slug, user):
        if user is not None:
            self.client.force_authenticate(TEST_USERS_LOCATIONS[user])

        response = self.client.get(
            self.URL.format(location=location_slug))
        assert_equal(expected_status, response.status_code)

    def test_that_anonymous_user_can_see_public_location(self):
        self.assert_status(200, 'location-public-1', user=None)

    def test_that_anonymous_user_cannot_see_private_location_http_401(self):
        self.assert_status(401, 'location-private-1', user=None)

    def test_that_user_can_access_own_location(self):
        self.assert_status(200, 'location-private-1', user='user-1')

    def test_that_user_without_correct_permission_gets_http_403(self):
        self.assert_status(403, 'location-private-2', user='user-1')

    def test_that_collector_user_can_access_public_location(self):
        self.assert_status(200, 'location-public-1', user='user-collector')

    def test_that_collector_user_can_access_private_location(self):
        self.assert_status(200, 'location-private-1', user='user-collector')


class TestTideLevelsPermissions(TestPermissionsMixin, APITestCase):
    URL = '/1/predictions/tide-levels/{location}/now/'
