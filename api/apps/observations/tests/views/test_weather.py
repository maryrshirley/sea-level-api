import copy
import json

from django.utils.translation import ugettext as _

from nose.tools import assert_equal
from nose_parameterized import parameterized

from rest_framework.test import APITestCase

from api.apps.locations.models import Location
from api.apps.users.helpers import create_user
from api.libs.test_utils import ViewAuthenticationTest
from api.libs.test_utils.datetime_utils import delta
from api.libs.param_parsers.parse_time import parse_datetime
from api.libs.view_helpers import format_datetime

from ...models import WeatherObservation


_URL = '/1/observations/weather/liverpool'
_URL_RECENT = _URL + '/recent'

WEATHER_A = {
    'precipitation': 7,
    'pressure': 8,
    'wind_gust': 9,
    'wind_speed': 10,
    'wind_direction': u'S',
    'wind_degrees': 12,
    'temperature': 13,
    'datetime': '2014-06-10T10:34:00Z',
}


def load_recent_test_cases():

    # now - VALID
    o = [(delta(), True)]

    # now(-1m) - VALID
    o.append((delta(minutes=-1), True))

    # now(+1m) - NOT VALID
    o.append((delta(minutes=1), False))

    # now(-1h) - VALID
    o.append((delta(hours=-1), True))

    # now(-2h) - VALID
    o.append((delta(hours=-2), True))

    # now(-24h) - VALID
    o.append((delta(hours=-24), True))

    # now(-24h +1m) - VALID
    o.append((delta(hours=-24, minutes=1), True))

    # now (-24h -1m) - NOT VALID
    o.append((delta(hours=-24, minutes=-1), False))

    return o


def load_recent_range_test_cases():

    # now - VALID
    o = [(delta(), delta(), True)]

    # now(-1h) -> now(-1m) - NOT VALID
    o.append((delta(hours=-1), delta(minutes=-1), False))

    # now(-1h) -> now() - VALID
    o.append((delta(hours=-1), delta(), True))

    # now(-1m) -> now() - VALID
    o.append((delta(minutes=-1), delta(), True))

    return o


def load_test_cases():
    cases = [(_URL, 'GET, POST, HEAD, OPTIONS',)]
    for uri in [key for key in WEATHER_A.keys() if not key == 'datetime']:
        uri = uri.replace('_', '-')
        cases.append(("{0}/{1}".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
        cases.append(("{0}/{1}/recent".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
    return cases


class TestWeatherView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestWeatherView, cls).setUpClass()
        cls.liverpool = Location.objects.create(slug='liverpool',
                                                name='Liverpool')
        cls.user = create_user('collector', is_internal_collector=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.liverpool.delete()
        super(TestWeatherView, cls).tearDownClass()

    def create_observation(self, **kwargs):
        data = copy.copy(WEATHER_A)
        data['location_id'] = self.liverpool.id
        data.update(**kwargs)
        return WeatherObservation.objects.create(**data)

    def create_observation_now(self, **kwargs):
        return self.create_observation(datetime=delta())

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @parameterized.expand(load_test_cases)
    def test_that_endpoint_exists(self, url, allow):
        observation = self.create_observation()
        response = self.client.options(url)
        assert_equal(200, response.status_code)
        observation.delete()

    @parameterized.expand(load_test_cases)
    def test_that_endpoint_returns_json(self, url, allow):
        response = self.client.get(url)
        json.loads(response.content.decode('utf-8'))

    def test_that_no_location_returns_400(self):
        response = self.client.get(_URL_RECENT.replace('/liverpool', ''))
        assert_equal(400, response.status_code)

    def test_that_invalid_location_returns_400(self):
        response = self.client.get(
            _URL_RECENT.replace('liverpool', 'badlocation'))
        assert_equal(400, response.status_code)

    @parameterized.expand(load_test_cases)
    def test_that_http_options_allowed(self, url, allow):
        response = self.client.options(url)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])

    def test_that_http_post_can_create_single_weather_observation(self):
        response = self.client.post(_URL, data=json.dumps([WEATHER_A]),
                                    content_type='application/json')
        assert_equal(201, response.status_code)

        assert_equal(1, WeatherObservation.objects.all().count())
        observation = WeatherObservation.objects.get()

        keys = map(lambda x: str.replace(x, 'datetime', 'minute__datetime'),
                   WEATHER_A.keys())
        serialized_data = WeatherObservation.objects.filter(id=observation.id) \
            .values(*keys)[0]
        serialized_data['datetime'] = serialized_data['minute__datetime']
        del serialized_data['minute__datetime']
        weather_data = copy.copy(WEATHER_A)
        weather_data['datetime'] = parse_datetime(weather_data['datetime'])
        assert_equal(weather_data, serialized_data)

    def test_that_http_get_returns_weather_observation(self):
        observation = self.create_observation_now()
        response = self.client.get(_URL_RECENT)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(1, len(data))
        observation.delete()

    def test_that_http_get_returns_multiple_weather_observations(self):
        observation1 = self.create_observation_now()
        observation2 = self.create_observation(datetime=delta(minutes=-1))

        response = self.client.get(_URL_RECENT)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(2, len(data))

        observation1.delete()
        observation2.delete()

    @parameterized.expand(load_recent_test_cases)
    def test_that_http_get_relevant_observation(self, _datetime, _valid):
        observation = self.create_observation(datetime=_datetime)

        response = self.client.get(_URL_RECENT)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(1 if _valid else 0, len(data))
        observation.delete()

    def test_that_http_get_range_prediction(self):
        prediction = self.create_observation_now()
        data = {'start': format_datetime(delta()),
                'end': format_datetime(delta())}
        response = self.client.get(_URL, data)
        assert_equal(200, response.status_code)

        prediction.delete()

    @parameterized.expand(load_recent_range_test_cases)
    def test_that_http_get_range_prediction_edges(self, _start, _end, _valid):
        prediction = self.create_observation(datetime=delta())
        payload = {'start': format_datetime(_start),
                   'end': format_datetime(_end)}
        response = self.client.get(_URL, payload)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))

        assert_equal(1 if _valid else 0, len(data))
        prediction.delete()

    def test_that_http_get_range_future_invalid(self):
        prediction = self.create_observation_now()
        payload = {'start': format_datetime(delta()),
                   'end': format_datetime(delta(minutes=1))}
        response = self.client.get(_URL, payload)
        prediction.delete()

        assert_equal(400, response.status_code)
        assert_equal(_(u'End range cannot be in the future'),
                     json.loads(response.content.decode('utf-8'))['detail'])

    def test_that_http_get_no_range_returns_bad_request(self):
        prediction = self.create_observation_now()
        data = {}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        prediction.delete()

    def test_that_http_get_no_start_returns_bad_request(self):
        prediction = self.create_observation_now()
        data = {'end': delta(hours=1)}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        prediction.delete()

    def test_that_http_get_no_end_returns_bad_request(self):
        prediction = self.create_observation_now()
        data = {'start': delta()}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        prediction.delete()


class TestWeatherTokenAuthentication(ViewAuthenticationTest):

    @classmethod
    def setUpClass(cls):
        super(TestWeatherTokenAuthentication, cls).setUpClass(_URL, WEATHER_A)

    def test_that_no_authentication_header_returns_http_401(self):
        self._test_that_no_authentication_header_returns_http_401()

    def test_that_user_without_add___permission_gets_403(self):
        self._test_that_user_without_add___permission_gets_403()

    def test_that_user_with_add__permission_can_post(self):
        self._test_that_user_with_add__permission_can_post()
