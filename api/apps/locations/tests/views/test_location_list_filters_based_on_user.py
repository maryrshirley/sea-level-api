from rest_framework.test import APITestCase

from nose.tools import assert_equal

from api.apps.users.helpers import create_user
from api.libs.test_utils import decode_json
from api.libs.test_utils.location import LocationMixin


class TestLocationListFiltering(APITestCase, LocationMixin):

    def setUp(self):
        super(TestLocationListFiltering, self).setUp()
        self.user_collector = create_user(
            'user-collector', is_internal_collector=True)
        self.location_public = self.create_location(slug='public-1',
                                                    visible=True)
        self.location_private_1 = self.create_location(slug='private-1',
                                                       visible=False)
        self.location_private_2 = self.create_location(slug='private-2',
                                                       visible=False)
        self.user_1 = create_user(
            'user-1', available_locations=[self.location_private_1])

        self.user_2 = create_user(
            'user-2',
            available_locations=[
                self.location_private_1, self.location_private_2]
        )

    def tearDown(self):
        self.location_public.delete()
        self.location_private_1.delete()
        self.location_private_2.delete()
        self.user_1.delete()
        self.user_2.delete()
        self.user_collector.delete()
        super(TestLocationListFiltering, self).tearDown()

    PATH = '/1/locations/'

    def _get_locations_for(self, user):
        if user is not None:
            self._become_user(user)
        return self._get_locations()

    def _become_user(self, user):
        self.client.force_authenticate(user)

    def _get_locations(self):
        response = self.client.get(self.PATH)
        assert_equal(200, response.status_code)
        return set([
            data['slug']
            for data in decode_json(response.content)['locations']
        ])

    def test_that_anonymous_user_sees_public_location(self):
        assert_equal(
            set(['public-1']),
            self._get_locations_for(None)
        )

    def test_that_user_1_sees_location_1(self):
        assert_equal(
            set(['private-1']),
            self._get_locations_for(self.user_1)
        )

    def test_that_user_2_sees_locations_1_and_2(self):
        assert_equal(
            set(['private-1', 'private-2']),
            self._get_locations_for(self.user_2)
        )

    def test_that_collector_user_sees_all_locations(self):
        assert_equal(
            set(['private-1', 'private-2', 'public-1']),
            self._get_locations_for(self.user_collector)
        )
