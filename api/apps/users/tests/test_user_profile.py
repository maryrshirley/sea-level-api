from django.contrib.auth.models import User
from django.test import TestCase
from nose.tools import assert_equal, assert_is_instance

from api.apps.users.models import UserProfile

NEW_USER = None


def setUpModule():
    global NEW_USER
    NEW_USER = User.objects.create(username='test_user')


def tearDownModule():
    if NEW_USER is not None:
        NEW_USER.delete()


class TestCreateUserProfile(TestCase):
    def test_that_new_user_has_user_profile(self):
        assert_is_instance(NEW_USER.user_profile, UserProfile)

    def test_that__is_internal_collector__defaults_to_false(self):
        assert_equal(False, NEW_USER.user_profile.is_internal_collector)

    def test_that__available_locations__defaults_to_empty(self):
        assert_equal(0, NEW_USER.user_profile.available_locations.count())
