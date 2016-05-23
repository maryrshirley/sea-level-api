import json

from django.conf import settings
from django.db.models.loading import get_model

from freezegun import freeze_time

from nose.tools import assert_equal
from nose_parameterized import parameterized
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.apps.users.helpers import create_user
from api.libs.test_utils.schedule import ScheduleMixin

_URL = ScheduleMixin.schedule_endpoint
_URL_LIVERPOOL = ScheduleMixin.schedule_departures_endpoint.format('liverpool')
_URL_HEYSHAM = ScheduleMixin.schedule_arrivals_endpoint.format('heysham')

url_testcases = [
    (_URL, 'POST, OPTIONS'),
    (_URL_LIVERPOOL, 'GET, HEAD, OPTIONS'),
    (_URL_HEYSHAM, 'GET, HEAD, OPTIONS'),
]


User = get_model('auth', 'User')


class TestSchedule(APITestCase, ScheduleMixin):

    @classmethod
    def setUpClass(cls):
        super(TestSchedule, cls).setUpClass()
        cls.permitted = create_user('permitted', is_internal_collector=True)
        cls.forbidden = create_user('forbidden', is_internal_collector=False)
        cls.token_permitted, _ = Token.objects.get_or_create(
            user=cls.permitted)
        cls.token_forbidden, _ = Token.objects.get_or_create(
            user=cls.forbidden)
        cls.token = cls.token_permitted

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

    @property
    def auth(self):
        return {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}

    @parameterized.expand(url_testcases)
    def test_that_endpoint_exists(self, url, allow):
        user = User.objects.get(username='permitted')
        token, _ = Token.objects.get_or_create(user=user)
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
                   self.payload_schedule(self.SCHEDULE_B)]

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

        response = self.client.options(_URL_LIVERPOOL)
        assert_equal(401, response.status_code)

        response = self.client.options(_URL_HEYSHAM)
        assert_equal(401, response.status_code)

    def test_that_user_without_add__permission_returns_403_status(self):
        payload = [self.payload_schedule()]
        self.postPayload(payload, 0, status=403, username='forbidden')

        self.token = self.token_forbidden
        response = self.client.options(_URL_LIVERPOOL, **self.auth)
        assert_equal(403, response.status_code)

        response = self.client.options(_URL_HEYSHAM, **self.auth)
        assert_equal(403, response.status_code)

    def assertGetSchedules(self, status_code, items, url=_URL_LIVERPOOL,
                           category='departure'):
        response = self.client.get(url, **self.auth)
        assert_equal(status_code, response.status_code)
        data = json.loads(response.content.decode('utf-8'))
        assert_equal(len(items), len(data))

        for index, item in enumerate(items):
            raw = item.__dict__
            if category == 'departure':
                departure = raw['_departure_cache'] \
                    .datetime.strftime(settings.DATETIME_FORMAT)
                record = {
                    u'vessel': unicode(raw['_vessel_cache'].name),
                    u'departure': unicode(departure)}
            else:
                arrival = raw['_arrival_cache'] \
                    .datetime.strftime(settings.DATETIME_FORMAT)
                record = {
                    u'vessel': unicode(raw['_vessel_cache'].name),
                    u'arrival': unicode(arrival)}
            assert_equal(record, data[index])

    def test_that_http_get_returns_record(self):
        payload = self.payload_schedule()
        schedule = self.create_schedule(payload=payload)
        with freeze_time(payload['departure'].datetime):
            self.assertGetSchedules(200, [schedule])
        schedule.delete()

    def test_that_http_get_relevant_schedules(self):
        payload = self.payload_schedule()
        schedule = self.create_schedule(payload=payload)
        with freeze_time(payload['departure'].datetime):
            self.assertGetSchedules(200, [schedule])
            self.assertGetSchedules(200, [schedule], url=_URL_HEYSHAM,
                                    category='arrival')

        schedule.delete()

    def test_that_http_get_ignores_past(self):
        schedule_old = self.create_schedule(
            departure_datetime='2016-03-26T08:00:00Z',
            arrival_datetime='2016-03-26T10:00:00Z')
        payload = self.payload_schedule()
        schedule = self.create_schedule(payload=payload)
        with freeze_time(payload['departure'].datetime):
            self.assertGetSchedules(200, [schedule])

        schedule.delete()
        schedule_old.delete()

    def test_that_http_orders_datetime(self):
        payload1 = self.payload_schedule(
            departure_datetime='2016-03-26T16:00:00Z',
            arrival_datetime='2016-03-26T18:00:00Z')
        payload2 = self.payload_schedule()
        schedule1 = self.create_schedule(payload=payload1)
        schedule2 = self.create_schedule(payload=payload2)

        with freeze_time(payload2['departure'].datetime):
            self.assertGetSchedules(200, [schedule2, schedule1])

        schedule1.delete()
        schedule2.delete()
