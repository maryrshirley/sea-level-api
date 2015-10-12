from rest_framework.test import APITestCase

from api.apps.predictions.tests.views.test_permissions import (
    TestPermissionsMixin, setUpModule as external_setUpModule,
    tearDownModule as external_tearDownModule)


def setUpModule():
    external_setUpModule()


def tearDownModule():
    external_tearDownModule()


class TestSeaLevelsPermissions(TestPermissionsMixin, APITestCase):
    URL = '/1/sea-levels/{location}/now/'
