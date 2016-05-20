import json

from django.db.models.loading import get_model

from nose.tools import assert_equal
from nose_parameterized import parameterized
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.apps.users.helpers import create_user
from api.libs.test_utils.schedule import (ScheduleRequirementsMixin,
                                          ScheduleMixin)

_URL = ScheduleMixin.schedule_endpoint

url_testcases = [
    (_URL, 'POST, OPTIONS'),
]


User = get_model('auth', 'User')


class TestSchedule(APITestCase, ScheduleRequirementsMixin):

    @classmethod
    def setUpClass(cls):
        super(TestSchedule, cls).setUpClass()
        cls.permitted = create_user('permitted', is_internal_collector=True)
        cls.forbidden = create_user('forbidden', is_internal_collector=False)

    @classmethod
    def tearDownClass(cls):
        cls.forbidden.delete()
        cls.permitted.delete()
        super(TestSchedule, cls).tearDownClass()

    def setUp(self):
        super(TestSchedule, self).setUp()
        self.setUpScheduleRequirements()

    def tearDown(self):
        self.tearDownScheduleRequirements()
        super(TestSchedule, self).tearDown()

    @parameterized.expand(url_testcases)
    def test_that_endpoint_exists(self, url, allow):
        user = User.objects.get(username='permitted')
        token, created = Token.objects.get_or_create(user=user)
        response = self.client.options(url,
                                       HTTP_AUTHORIZATION='Token ' + token.key)
        assert_equal(200, response.status_code)

    @parameterized.expand(url_testcases)
    def test_that_http_options_allowed(self, url, allow):
        user = User.objects.get(username='permitted')
        token, created = Token.objects.get_or_create(user=user)
        response = self.client.options(url,
                                       HTTP_AUTHORIZATION='Token ' + token.key)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])

    def postPayload(self, payload, count, status=201, username='permitted'):
        if type(payload) is list:
            payload = [self.values_payload(x) for x in payload]
        else:
            payload = self.values_payload(payload)

        data = json.dumps(payload)
        url = _URL

        extra = {}
        if username:
            user = User.objects.get(username=username)
            token, created = Token.objects.get_or_create(user=user)
            extra = {'HTTP_AUTHORIZATION': 'Token ' + token.key}

        response = self.client.post(url, data=data,
                                    content_type='application/json',
                                    **extra)
        self.assertEqual(status, response.status_code)

        self.assertEqual(count, self.objects.all().count())

        # XXX: Check payload matches

    def test_that_http_post_can_create_single_schedule(self):
        payload = [self.payload_schedule()]
        self.postPayload(payload, 1)

    def test_that_http_post_can_create_multiple_schedules(self):
        payload = [self.payload_schedule(),
                   self.payload_schedule(self.DATA_B)]

        self.postPayload(payload, 2)

    def test_that_http_post_replaces_existing_schedule(self):
        payload = [self.payload_schedule()]
        self.postPayload(payload, 1)

        payload = [self.payload_schedule(
            departure__datetime='2016-03-26T12:05:00Z',
            arrival__datetime='2016-03-26T14:05:00Z')]
        self.postPayload(payload, 1)

        # XXX: Check the values have changed

        '''
            What can update?
                A schedule can be cancelled
                Times can vary (increase/decrease)
                Origin/destination can change
                Vessel IMO can change
        '''

    def test_that_http_post_add_replace_mixed(self):
        pass

    def test_that_http_post_duplicate_create_single_schedule(self):
        payload = [self.payload_schedule(),
                   self.payload_schedule()]
        self.postPayload(payload, 1)

    def test_that_dictionary_returns_201_status(self):
        payload = self.payload_schedule()
        self.postPayload(payload, 1, status=201)

    def test_that_invalid_imo_returns_400_status(self):
        payload = [self.payload_schedule(vessel__imo='1234567')]
        self.postPayload(payload, 0, status=400)

    def test_that_invalid_locations_returns_400_status(self):
        payload = [self.payload_schedule(destination__slug='invalid')]
        self.postPayload(payload, 0, status=400)

        payload = [self.payload_schedule(origin__slug='invalid')]
        self.postPayload(payload, 0, status=400)

    def test_that_invalid_datetime_returns_400_status(self):
        payload = [self.payload_schedule(
            departure__datetime='2016-03-32T12:05:00Z')]
        self.postPayload(payload, 0, status=400)

    def test_that_no_authentication_returns_401_status(self):
        payload = [self.payload_schedule()]
        self.postPayload(payload, 0, status=401, username=None)

    def test_that_user_without_add__permission_returns_403_status(self):
        payload = [self.payload_schedule()]
        self.postPayload(payload, 0, status=403, username='forbidden')
