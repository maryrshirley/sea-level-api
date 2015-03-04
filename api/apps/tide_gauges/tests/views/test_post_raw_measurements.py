import json

from nose.tools import assert_equal

from django.conf import settings

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from api.libs.test_utils import (decode_json, make_permitted_forbidden_users,
                                 delete_users)

from api.apps.tide_gauges.models import (RawMeasurement, TideGauge,
                                         TideGaugeLocationLink)
from api.apps.observations.models import Observation
from api.apps.locations.models import Location


_URL = '/1/tide-gauges/raw-measurements/gladstone/'


def assert_json_response(response, expected_json=None, expected_status=201):
    assert_equal(expected_status, response.status_code)
    if expected_json is not None:
        assert_equal(expected_json, decode_json(response.content))


class TestPutRawMeasurementsBase(APITestCase):
    @classmethod
    def setUpClass(cls):
        TideGauge.objects.all().delete()
        TideGauge.objects.create(slug='gladstone')
        (cls.permitted, cls.forbidden) = make_permitted_forbidden_users(
            ['add_rawmeasurement'])

    @classmethod
    def tearDownClass(cls):
        TideGauge.objects.all().delete()
        delete_users()

    def _post_json(self, data, **extras):
        return self.client.post(
            _URL,
            data=json.dumps(data),
            content_type='application/json',
            **extras)

    @staticmethod
    def _serialize(obj):
        """
        Serialize a RawMeasurement or Observation
        """
        if isinstance(obj, RawMeasurement):
            return {
                'datetime': obj.datetime.strftime(
                    settings.DATETIME_FORMAT),
                'height': obj.height
            }
        elif isinstance(obj, Observation):
            return {
                'datetime': obj.minute.datetime.strftime(
                    settings.DATETIME_FORMAT),
                'location': obj.location.slug,
                'height': obj.sea_level
            }
        else:
            raise TypeError("Can't serialize a {}".format(type(obj)))


class TestPostRawMeasurements(TestPutRawMeasurementsBase):
    PREDICTION_A = {
        "datetime": "2014-06-10T10:34:00Z",
        "height": 0.23
    }

    PREDICTION_B = {
        "datetime": "2014-06-10T10:34:00Z",  # same as A
        "height": -0.15
    }

    PREDICTION_C = {
        "datetime": "2014-06-10T11:00:00Z",
        "height": 0.50
    }

    def setUp(self):
        self.client.force_authenticate(self.permitted)
        RawMeasurement.objects.all().delete()

    def test_that_http_options_allowed_methods_are_post_and_options(self):
        response = self.client.options(_URL)
        assert_equal(200, response.status_code)
        assert_equal('POST, OPTIONS', response['Allow'])

    def test_that_http_get_is_not_allowed(self):
        response = self.client.get(_URL)
        assert_equal(405, response.status_code)
        assert_equal(
            {'detail': "Method 'GET' not allowed."},
            decode_json(response.content))

    def test_that_valid_http_post_returns_json_message(self):
        response = self._post_json([self.PREDICTION_A])
        assert_json_response(response, expected_json=[
            {
                'datetime': '2014-06-10T10:34:00Z',
                'height': 0.23,
            }
        ])

    def test_that_valid_http_post_returns_http_201_created(self):
        response = self._post_json([self.PREDICTION_A])
        assert_json_response(response, expected_status=201)

    def test_that_passing_a_non_list_json_object_gives_sane_error(self):
        response = self._post_json(self.PREDICTION_A)

        assert_equal(400, response.status_code)
        assert_equal(
            {'non_field_errors': [
                'Expected a list of items but got type `dict`.']},
            decode_json(response.content))

    def test_that_http_post_can_create_single_measurement(self):
        response = self._post_json([self.PREDICTION_A])
        assert_json_response(response, expected_status=201)

        assert_equal(1, RawMeasurement.objects.all().count())
        assert_equal(self.PREDICTION_A,
                     self._serialize(RawMeasurement.objects.all()[0]))

    def test_that_http_post_can_create_multiple_measurements(self):
        response = self._post_json([self.PREDICTION_A, self.PREDICTION_C])

        assert_json_response(response, expected_status=201)
        assert_equal(2, RawMeasurement.objects.all().count())

        ob_1, ob_2 = RawMeasurement.objects.all()
        assert_equal(self.PREDICTION_A, self._serialize(ob_1))
        assert_equal(self.PREDICTION_C, self._serialize(ob_2))

    def test_that_http_post_can_overwrite_measurement(self):
        response = self._post_json([self.PREDICTION_A])
        assert_json_response(response, expected_status=201)

        response = self._post_json([self.PREDICTION_B])
        assert_json_response(response, expected_status=201)

        assert_equal(1, RawMeasurement.objects.all().count())
        assert_equal(self.PREDICTION_B,
                     self._serialize(RawMeasurement.objects.all()[0]))

    def test_that_one_bad_record_causes_all_records_to_fail(self):
        bad = {'datetime': 'invalid', 'height': 0.23}
        response = self._post_json(
            [self.PREDICTION_A, bad])
        assert_equal(400, response.status_code)
        assert_equal(0, RawMeasurement.objects.all().count())

    def test_that_datetime_without_timezone_is_rejected(self):
        doc = {
            "datetime": "2014-06-10T10:34:00",
            "height": 0.23
        }
        response = self._post_json([doc])
        assert_equal(400, response.status_code)
        assert_equal(
            [{
                'datetime': ['Datetime has wrong format. Use one of these '
                             'formats instead: YYYY-MM-DDThh:mm:00Z']
            }],
            decode_json(response.content))

    def test_that_datetime_with_non_utc_timezone_is_rejected(self):
        doc = {
            "datetime": "2014-06-10T10:34:00+02:00",
            "height": 0.23
        }
        response = self._post_json([doc])
        assert_equal(400, response.status_code)
        assert_equal(
            [{
                'datetime': ['Datetime has wrong format. Use one of these '
                             'formats instead: YYYY-MM-DDThh:mm:00Z']
            }],
            decode_json(response.content))

    def test_that_datetime_with_seconds_is_rejected(self):
        doc = {
            "datetime": "2014-06-10T10:34:45Z",
            "height": 0.23
        }
        response = self._post_json([doc])
        assert_equal(400, response.status_code)
        assert_equal(
            [{
                'datetime': ['Datetime has wrong format. Use one of these '
                             'formats instead: YYYY-MM-DDThh:mm:00Z']
            }],
            decode_json(response.content))


class TestTideGaugeLocationLink(TestPutRawMeasurementsBase):
    PREDICTION_A = {
        "datetime": "2014-06-10T10:34:00Z",
        "height": 0.23
    }
    PREDICTION_B = {
        "datetime": "2014-06-10T10:34:00Z",
        "height": 1.45
    }

    def setUp(self):
        self._clean_up()
        self.client.force_authenticate(self.permitted)

        self.location_1 = Location.objects.create(slug='location_1')
        self.location_2 = Location.objects.create(slug='location_2')

        TideGaugeLocationLink.objects.create(
            tide_gauge=TideGauge.objects.get(slug='gladstone'),
            location=self.location_2)

    def tearDown(self):
        self._clean_up()

    def _clean_up(self):
        RawMeasurement.objects.all().delete()
        Observation.objects.all().delete()
        TideGaugeLocationLink.objects.all().delete()

    def test_that_creating_raw_measurement_creates_linked_observation(self):
        response = self._post_json([self.PREDICTION_A])
        assert_json_response(response, expected_status=201)

        all_observations = Observation.objects.all()
        assert_equal(1, all_observations.count())

        expected = self.PREDICTION_A
        expected.update({'location': 'location_2'})

        assert_equal(
            expected,
            self._serialize(all_observations[0]))

    def test_that_linked_observation_gets_updated(self):
        self._post_json([self.PREDICTION_A])
        self._post_json([self.PREDICTION_B])  # update

        all_observations = Observation.objects.all()
        assert_equal(1, all_observations.count())

        expected = self.PREDICTION_B
        expected.update({'location': 'location_2'})

        assert_equal(
            expected,
            self._serialize(all_observations[0]))


class TestRawMeasurementsEndpointAuthentication(TestPutRawMeasurementsBase):
    def setUp(self):
        self.good_data = {
            "datetime": "2014-06-10T10:34:00Z",
            "height": 0.23
        }

    def test_that_no_authentication_header_returns_http_401(self):
        # 401 vs 403: http://stackoverflow.com/a/6937030
        response = self._post_json([])
        assert_equal(401, response.status_code)

    def test_that_user_without__add_surgeprediction__permission_gets_403(self):
        token = Token.objects.get(user__username='forbidden').key
        response = self._post_json(
            [self.good_data], HTTP_AUTHORIZATION='Token {}'.format(token))
        assert_json_response(response, expected_status=403, expected_json={
            'detail': 'You do not have permission to perform this action.'},
        )

    def test_that_user_with__add_surgeprediction__permission_can_post(self):
        token = Token.objects.get(user__username='permitted').key
        response = self._post_json(
            [self.good_data], HTTP_AUTHORIZATION='Token {}'.format(token))
        assert_json_response(response, expected_status=201)
