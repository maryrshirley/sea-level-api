from django.contrib.auth.models import User
from django.test import TestCase
from nose.tools import assert_equal, assert_is_instance

from api.apps.users.models import UserProfile


class TestCreateUserProfile(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username='test_user')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_that_new_user_has_user_profile(self):
        assert_is_instance(self.user.user_profile, UserProfile)

    def test_that__is_internal_collector__defaults_to_false(self):
        assert_equal(False, self.user.user_profile.is_internal_collector)

    def test_that__available_locations__defaults_to_empty(self):
        assert_equal(0, self.user.user_profile.available_locations.count())
