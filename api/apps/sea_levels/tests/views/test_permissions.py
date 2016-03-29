from rest_framework.test import APITestCase

from api.apps.predictions.tests.views.test_permissions import (
    TestPermissionsMixin)


class TestSeaLevelsPermissions(TestPermissionsMixin, APITestCase):
    URL = '/1/sea-levels/{location}/now/'

    def test_that_anonymous_user_can_see_public_location(self):
        self._test_that_anonymous_user_can_see_public_location()

    def test_that_anonymous_user_cannot_see_private_location_http_401(self):
        self._test_that_anonymous_user_cannot_see_private_location_http_401()

    def test_that_user_can_access_own_location(self):
        self._test_that_user_can_access_own_location()

    def test_that_user_without_correct_permission_gets_http_403(self):
        self._test_that_user_without_correct_permission_gets_http_403()

    def test_that_collector_user_can_access_public_location(self):
        self._test_that_collector_user_can_access_public_location()

    def test_that_collector_user_can_access_private_location(self):
        self._test_that_collector_user_can_access_private_location()
