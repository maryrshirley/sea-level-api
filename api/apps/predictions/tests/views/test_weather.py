import copy
import json

from django.core.exceptions import ValidationError

from nose.tools import assert_equal
from nose_parameterized import parameterized

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from api.apps.locations.models import Location
from api.apps.predictions.models import WeatherPrediction
from api.apps.users.helpers import create_user
from api.libs.param_parsers.parse_time import parse_datetime
from api.libs.test_utils import decode_json
from api.libs.test_utils.datetime_utils import delta
from api.libs.test_utils.weather import (PREDICTION_WEATHER,
                                         CreatePredictionMixin)
from api.libs.view_helpers import format_datetime

_URL = '/1/predictions/weather/liverpool'
_URL_NOW = _URL + '/now'


def load_now_test_cases():

    # now -> +2h - VALID
    o = [(delta(), delta(hours=2), True)]

    # ? -> now + 1m - VALID
    o.append((delta(hours=-2, minutes=1), delta(minutes=1), True))

    # ? -> now - 1m
    o.append((delta(hours=-2, minutes=-1), delta(minutes=-1), False))

    # now -1m -> ? - VALID
    o.append((delta(minutes=-1), delta(hours=2, minutes=-1), True))

    # now +1m -> ? - VALID
    o.append((delta(minutes=1), delta(hours=2, minutes=1), True))

    # now +0.5 -> ? - VALID
    o.append((delta(hours=1), delta(hours=3), True))

    # ?  -> +24h - 1m - VALID
    o.append((delta(hours=22, minutes=-1), delta(hours=24, minutes=-1), True))

    # ? -> +24h - VALID
    o.append((delta(hours=22), delta(hours=24), True))

    # ? -> +24h + 1m - VALID
    o.append((delta(hours=22, minutes=1), delta(hours=24, minutes=1), True))

    # +24 - 1m -> ? - VALID
    o.append((delta(hours=24, minutes=-1), delta(hours=26, minutes=-1), True))

    # +24h -> ? - VALID
    o.append((delta(hours=24), delta(hours=26), True))

    # +24h + 1m -> ? - NOT VALID
    # o.append((delta(hours=24, minutes=1), delta(hours=26, minutes=1), False))

    return o


def load_test_cases():
    cases = [(_URL, 'GET, POST, HEAD, OPTIONS',)]
    for uri in [key for key in PREDICTION_WEATHER.keys() if key not in
                ['datetime', 'supplier', 'valid_from', 'valid_to']]:
        uri = uri.replace('_', '-')
        cases.append(("{0}/{1}".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
        cases.append(("{0}/{1}/now".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
        cases.append(("{0}/{1}/latest".format(_URL, uri),
                     'GET, HEAD, OPTIONS',))
    return cases


class PostJsonMixin(object):
    def _post_json(self, data, url=_URL, **extras):
        return self.client.post(url,
                                data=json.dumps(data),
                                content_type='application/json',
                                **extras)


class TestWeatherView(APITestCase, PostJsonMixin, CreatePredictionMixin):

    @classmethod
    def setUpClass(cls):
        cls.liverpool = Location.objects.create(
            slug='liverpool', name='Liverpool')
        cls.location = cls.liverpool

        cls.user = create_user('collector', is_internal_collector=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.liverpool.delete()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @staticmethod
    def _serialize(prediction, keys):
        return WeatherPrediction.objects.filter(id=prediction.id).values(*keys)

    @parameterized.expand(load_test_cases)
    def test_that_endpoint_exists(self, url, allow):
        response = self.client.options(url)
        assert_equal(200, response.status_code)

    def test_that_http_post_can_create_single_weather_prediction(self):
        response = self._post_json([PREDICTION_WEATHER])
        assert_equal(201, response.status_code)

        assert_equal(1, WeatherPrediction.objects.all().count())
        keys = map(lambda x: str.replace(x,
                                         'valid_to',
                                         'minute_to__datetime'),
                   PREDICTION_WEATHER.keys())
        keys = map(lambda x: str.replace(x,
                                         'valid_from',
                                         'minute_from__datetime'),
                   keys)

        prediction = WeatherPrediction.objects.get()
        ser_data = self._serialize(prediction, keys)[0]
        ser_data['valid_from'] = ser_data['minute_from__datetime']
        ser_data['valid_to'] = ser_data['minute_to__datetime']
        del ser_data['minute_from__datetime']
        del ser_data['minute_to__datetime']

        weather_data = copy.copy(PREDICTION_WEATHER)
        weather_data['valid_from'] = parse_datetime(weather_data['valid_from'])
        weather_data['valid_to'] = parse_datetime(weather_data['valid_to'])

        assert_equal(weather_data, ser_data)

    def test_that_http_get_invalid_location_errors(self):
        response = self.client.get(_URL_NOW.replace('liverpool', 'badname'))
        assert_equal(400, response.status_code)

    def test_that_http_post_invalid_location_errors(self):
        response = self._post_json([PREDICTION_WEATHER],
                                   _URL.replace('liverpool', 'badname'))
        assert_equal(400, response.status_code)

    @parameterized.expand(load_test_cases)
    def test_that_http_options_allowed_methods(self, url, allow):
        response = self.client.options(url)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])

    def test_that_http_get_returns_single_weather_prediction(self):
        prediction = self.create_prediction_now()

        response = self.client.get(_URL_NOW)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(1, len(data))
        prediction.delete()

    def test_that_default_weather_type_is_unavailable(self):
        WeatherPrediction.objects.create(precipitation=20,
                                         location=self.location,
                                         pressure=21,
                                         wind_gust=22,
                                         wind_direction='N',
                                         wind_degrees=24,
                                         wind_speed=25,
                                         temperature=26,
                                         supplier='met_office',
                                         valid_from=delta(hours=2),
                                         valid_to=delta(hours=4))
        prediction = WeatherPrediction.objects.get()
        self.assertEquals('not_available', prediction.weather_type)

    def test_that_http_get_returns_multiple_weather_prediction(self):
        prediction1 = self.create_prediction_now()
        prediction2 = \
            self.create_prediction_now(precipitation=20,
                                       pressure=21,
                                       wind_gust=22,
                                       wind_direction='N',
                                       wind_degrees=24,
                                       wind_speed=25,
                                       temperature=26,
                                       supplier='met_office',
                                       weather_type='thunder',
                                       valid_from=delta(hours=2),
                                       valid_to=delta(hours=4))

        response = self.client.get(_URL_NOW)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(2, len(data))
        prediction1.delete()
        prediction2.delete()

    def test_that_http_get_returns_multiple_relevant_now_predictions(self):
        prediction1 = self.create_prediction_now()
        prediction2 = self.create_prediction(valid_from=delta(hours=-4),
                                             valid_to=delta(hours=-2))
        prediction3 = self.create_prediction(valid_from=delta(hours=4),
                                             valid_to=delta(hours=6))

        response = self.client.get(_URL_NOW)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(2, len(data))

        prediction1.delete()
        prediction2.delete()
        prediction3.delete()

    @parameterized.expand(load_now_test_cases)
    def test_that_http_get_relevant_now_prediction(self, _from, _to, _valid):
        prediction = self.create_prediction(valid_from=_from,
                                            valid_to=_to)

        response = self.client.get(_URL_NOW)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))
        assert_equal(1 if _valid else 0, len(data))
        prediction.delete()

    def test_that_http_get_range_prediction(self):
        prediction = self.create_prediction_now()
        data = {'start': format_datetime(delta()),
                'end': format_datetime(delta(hours=1))}
        response = self.client.get(_URL, data)
        assert_equal(200, response.status_code)

        prediction.delete()

    @parameterized.expand(load_now_test_cases)
    def test_that_http_get_range_prediction_edges(self, _from, _to, _valid):
        prediction = self.create_prediction(valid_from=delta(),
                                            valid_to=delta(hours=24))
        payload = {'start': format_datetime(_from),
                   'end': format_datetime(_to)}
        response = self.client.get(_URL, payload)
        assert_equal(200, response.status_code)

        data = json.loads(response.content.decode('utf-8'))

        assert_equal(1 if _valid else 0, len(data))
        prediction.delete()

    def test_that_http_get_no_range_returns_bad_request(self):
        prediction = self.create_prediction_now()
        data = {}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        prediction.delete()

    def test_that_http_get_no_start_returns_bad_request(self):
        prediction = self.create_prediction_now()
        data = {'end': delta(hours=1)}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        prediction.delete()

    def test_that_http_get_no_end_returns_bad_request(self):
        prediction = self.create_prediction_now()
        data = {'start': delta()}
        response = self.client.get(_URL, data)
        assert_equal(400, response.status_code)

        prediction.delete()

    def test_that_duplicate_records_raise(self):
        prediction = self.create_prediction()
        with self.assertRaises(ValidationError) as validationError:
            self.create_prediction()
        error_base = 'Weather prediction with this Location and Minute {0}'\
            ' already exists.'
        error1 = error_base.format('from')
        error2 = error_base.format('to')
        errors = validationError.exception.message_dict['__all__']
        self.assertEquals(error1, errors[0])
        self.assertEquals(error2, errors[1])
        prediction.delete()

    def test_that_duplicate_from_raises(self):
        prediction = self.create_prediction()
        with self.assertRaises(ValidationError) as validationError:
            self.create_prediction(valid_to=delta())
        error_base = 'Weather prediction with this Location and Minute {0}'\
            ' already exists.'
        error1 = error_base.format('from')
        errors = validationError.exception.message_dict['__all__']
        self.assertEquals(error1, errors[0])
        prediction.delete()

    def test_that_duplicate_to_raises(self):
        prediction = self.create_prediction()
        with self.assertRaises(ValidationError) as validationError:
            self.create_prediction(valid_from=delta())
        error_base = 'Weather prediction with this Location and Minute {0}'\
            ' already exists.'
        error1 = error_base.format('to')
        errors = validationError.exception.message_dict['__all__']
        self.assertEquals(error1, errors[0])
        prediction.delete()

    def test_that_existing_objects_order_by_datetime(self):
        prediction1 = self.create_prediction(valid_from=delta(hours=4),
                                             valid_to=delta(hours=6))
        prediction2 = self.create_prediction(valid_from=delta(hours=2),
                                             valid_to=delta(hours=4))

        predictions = WeatherPrediction.objects.now_plus_24(self.liverpool)

        self.assertEqual(prediction2, predictions[0])
        self.assertEqual(prediction1, predictions[1])

        prediction2.delete()
        prediction1.delete()


class TestWeatherTokenAuthentication(APITestCase, PostJsonMixin):
    @classmethod
    def setUpClass(cls):
        cls.liverpool = Location.objects.create(
            slug='liverpool', name='Liverpool')
        cls.location = cls.liverpool
        cls.permitted = create_user('permitted', is_internal_collector=True)
        cls.forbidden = create_user('forbidden', is_internal_collector=False)

        cls.good_data = PREDICTION_WEATHER

    @classmethod
    def tearDownClass(cls):
        cls.permitted.delete()
        cls.forbidden.delete()
        cls.liverpool.delete()

    def test_that_no_authentication_header_returns_http_401(self):
        # 401 vs 403: http://stackoverflow.com/a/6937030
        response = self._post_json([])
        assert_equal(401, response.status_code)

    def test_that_user_without__add_weather__permission_gets_403(self):
        token = Token.objects.get(user__username='forbidden').key
        response = self._post_json(
            [self.good_data], HTTP_AUTHORIZATION='Token {}'.format(token))
        assert_equal(403, response.status_code)
        assert_equal(
            {'detail': 'You do not have permission to perform this action.'},
            decode_json(response.content))

    def test_that_user_with__add_weather__permission_can_post(self):
        token = Token.objects.get(user__username='permitted').key
        response = self._post_json(
            self.good_data, HTTP_AUTHORIZATION='Token {}'.format(token))
        assert_equal(201, response.status_code)
