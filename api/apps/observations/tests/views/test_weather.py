import copy
import json

from django.core.exceptions import ValidationError
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
from api.libs.test_utils.weather import (OBSERVATION_WEATHER,
                                         CreateObservationMixin)

from ...models import WeatherObservation


_URL = '/1/observations/weather/liverpool'
_URL_RECENT = _URL + '/recent'


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
    keys = OBSERVATION_WEATHER.keys()
    for uri in [key for key in keys if not key == 'datetime']:
        uri = uri.replace('_', '-')
        cases.append(("{0}/{1}".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
        cases.append(("{0}/{1}/recent".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
    return cases


class TestWeatherView(APITestCase, CreateObservationMixin):

    @classmethod
    def setUpClass(cls):
        super(TestWeatherView, cls).setUpClass()
        cls.liverpool = Location.objects.create(slug='liverpool',
                                                name='Liverpool')
        cls.location = cls.liverpool
        cls.user = create_user('collector', is_internal_collector=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.liverpool.delete()
        super(TestWeatherView, cls).tearDownClass()

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
        data = json.dumps([OBSERVATION_WEATHER])
        response = self.client.post(_URL, data=data,
                                    content_type='application/json')
        assert_equal(201, response.status_code)

        assert_equal(1, WeatherObservation.objects.all().count())
        observation = WeatherObservation.objects.get()

        keys = map(lambda x: str.replace(x, 'datetime', 'minute__datetime'),
                   OBSERVATION_WEATHER.keys())
        serialized_data = WeatherObservation.objects.filter(id=observation.id) \
            .values(*keys)[0]
        serialized_data['datetime'] = serialized_data['minute__datetime']
        del serialized_data['minute__datetime']
        weather_data = copy.copy(OBSERVATION_WEATHER)
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

    '''
    @parameterized.expand(load_recent_test_cases)
    def test_that_http_get_relevant_observation(self, _datetime, _valid):
        observation = self.create_observation(datetime=_datetime)

        response = self.client.get(_URL_RECENT)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(1 if _valid else 0, len(data))
        observation.delete()
    '''

    def test_that_http_get_range_observation(self):
        observation = self.create_observation_now()
        data = {'start': format_datetime(delta()),
                'end': format_datetime(delta())}
        response = self.client.get(_URL, data)
        assert_equal(200, response.status_code)

        observation.delete()

    '''
    @parameterized.expand(load_recent_range_test_cases)
    def test_that_http_get_range_observation_edges(self, _start, _end, _valid):
        observation = self.create_observation(datetime=delta())
        payload = {'start': format_datetime(_start),
                   'end': format_datetime(_end)}
        response = self.client.get(_URL, payload)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))

        assert_equal(1 if _valid else 0, len(data))
        observation.delete()
    '''

    def test_that_http_get_range_future_invalid(self):
        observation = self.create_observation_now()
        payload = {'start': format_datetime(delta()),
                   'end': format_datetime(delta(minutes=1))}
        response = self.client.get(_URL, payload)
        observation.delete()

        assert_equal(400, response.status_code)
        assert_equal(_(u'End range cannot be in the future'),
                     json.loads(response.content.decode('utf-8'))['detail'])

    def test_that_http_get_no_range_returns_bad_request(self):
        observation = self.create_observation_now()
        data = {}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        observation.delete()

    def test_that_http_get_no_start_returns_bad_request(self):
        observation = self.create_observation_now()
        data = {'end': delta(hours=1)}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        observation.delete()

    def test_that_http_get_no_end_returns_bad_request(self):
        observation = self.create_observation_now()
        data = {'start': delta()}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        observation.delete()

    def test_that_duplicate_records_raise(self):
        observation = self.create_observation()
        with self.assertRaises(ValidationError) as validationError:
            self.create_observation()
        error = u'Weather observation with this Location and Minute'\
            ' already exists.'
        errors = validationError.exception.message_dict['__all__']
        self.assertEquals(error, errors[0])
        observation.delete()

    def test_that_existing_objects_order_by_datetime(self):
        observation1 = self.create_observation(datetime=delta(hours=-4))
        observation2 = self.create_observation(datetime=delta(hours=-2))

        observations = WeatherObservation.objects.now_minus_24(self.liverpool)

        self.assertEqual(observation2, observations[0])
        self.assertEqual(observation1, observations[1])

        observation2.delete()
        observation1.delete()


class TestWeatherTokenAuthentication(ViewAuthenticationTest):

    @classmethod
    def setUpClass(cls):
        super(TestWeatherTokenAuthentication, cls) \
            .setUpClass(_URL, OBSERVATION_WEATHER)

    def test_that_no_authentication_header_returns_http_401(self):
        self._test_that_no_authentication_header_returns_http_401()

    def test_that_user_without_add___permission_gets_403(self):
        self._test_that_user_without_add___permission_gets_403()

    def test_that_user_with_add__permission_can_post(self):
        self._test_that_user_with_add__permission_can_post()
