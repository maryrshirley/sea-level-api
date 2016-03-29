import copy

from dateutil.parser import parse as parse_dt

from nose.tools import assert_equal, assert_in, assert_is_instance

from rest_framework.test import APITestCase

from api.libs.test_utils import (assert_json_response, decode_json,
                                 DatetimeParameterTestsMixin)
from api.apps.tide_gauges.models import RawMeasurement, TideGauge
from api.apps.users.helpers import get_or_create_user


BASE_PATH = '/1/tide-gauges/raw-measurements/'
PATH = BASE_PATH + 'gladstone-1/'

MEASUREMENTS = [
    {
        "tide_gauge__slug": 'gladstone-1',
        "datetime": parse_dt("2014-06-10T10:00:00Z"),
        "height": 1.23
    },
    {
        "tide_gauge__slug": 'gladstone-1',
        "datetime": parse_dt("2014-06-10T10:30:00Z"),
        "height": 1.56
    },

    {
        "tide_gauge__slug": 'gladstone-2',
        "datetime": parse_dt("2014-06-10T10:00:00Z"),
        "height": 5.67
    },
    {
        "tide_gauge__slug": 'gladstone-2',
        "datetime": parse_dt("2014-06-10T10:30:00Z"),
        "height": 5.89
    },
]


class CollectorAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(CollectorAPITestCase, cls).setUpClass()
        # https://docs.python.org
        # /3/library/unittest.html#setupmodule-and-teardownmodule

        cls.gladstone1, c = TideGauge.objects.get_or_create(slug='gladstone-1')
        cls.gladstone2, c = TideGauge.objects.get_or_create(slug='gladstone-2')

        cls.collector_user = get_or_create_user('user-collector',
                                                is_internal_collector=True)

        for m in copy.deepcopy(MEASUREMENTS):
            tide_gauge = TideGauge.objects.get(slug=m.pop('tide_gauge__slug'))
            m['tide_gauge'] = tide_gauge

            RawMeasurement.objects.get_or_create(**m)

    @classmethod
    def tearDownClass(cls):
        RawMeasurement.objects.all().delete()
        cls.collector_user.delete()

        cls.gladstone1.delete()
        cls.gladstone2.delete()
        super(CollectorAPITestCase, cls).tearDownClass()


class TestStartParameterValidation(CollectorAPITestCase,
                                   DatetimeParameterTestsMixin):
    def setUp(self):
        self.client.force_authenticate(self.collector_user)

    TEST_PATH = PATH + '?start={test_datetime}&end=2014-01-01T00:00:00Z'


class TestEndParameterValidation(CollectorAPITestCase,
                                 DatetimeParameterTestsMixin):
    def setUp(self):
        self.client.force_authenticate(self.collector_user)

    TEST_PATH = PATH + '?start=2014-01-01T00:00:00Z&end={test_datetime}'


class TestErrorHandling(CollectorAPITestCase):
    def setUp(self):
        self.client.force_authenticate(self.collector_user)

    def test_that_no_gauge_in_url_gives_an_http_404_with_json(self):
        expected = {'detail': 'No tide gauge specified in URL.'}
        assert_json_response(
            self.client.get(BASE_PATH), 404, expected)

    def test_that_a_non_existent_gauge_gives_an_http_404_with_json(self):
        expected = {'detail': 'Tide gauge not found: `no-such-gauge`.'}
        assert_json_response(
            self.client.get(BASE_PATH + 'no-such-gauge/'), 404, expected)

    def test_that_start_and_end_more_than_24_hours_gives_http_400_json(self):
        expected = {'detail': '`start` and `end` must be no greater than 24 '
                              'hours apart'}
        path = PATH + '?start=2014-01-01T00:00:00Z&end=2014-01-02T00:01:00Z'
        assert_json_response(self.client.get(path), 400, expected)

    def test_that_missing_start_parameter_has_json_400_error(self):
        expected = {'detail': 'Missing parameter `start`. '
                              'Format: 2014-11-30T00:00:00Z'}

        path = PATH + '?end=2014-01-02T00:00:00'
        assert_json_response(self.client.get(path), 400, expected)

    def test_that_missing_end_parameter_has_json_400_error(self):
        expected = {'detail': 'Missing parameter `end`. '
                              'Format: 2014-11-30T00:00:00Z'}

        path = PATH + '?start=2014-01-02T00:00:00'
        assert_json_response(self.client.get(path), 400, expected)


class TestResultStructure(CollectorAPITestCase):

    def setUp(self):
        self.client.force_authenticate(self.collector_user)
        path = PATH + '?start=2014-06-10T10:00:00Z&end=2014-06-10T10:01:00Z'
        self.data = decode_json(self.client.get(path).content)

    def test_that_envelope_has_raw_measurements_field(self):
        assert_in('raw_measurements', self.data)

    def test_that_records_have_correct_fields(self):
        assert_equal(
            set(['datetime', 'height']),
            set(self.data['raw_measurements'][0].keys()))

    def test_that_datetime_has_correct_format(self):
        assert_equal(
            '2014-06-10T10:00:00Z',
            self.data['raw_measurements'][0]['datetime'])

    def test_that_height_field_is_a_float(self):
        assert_is_instance(
            self.data['raw_measurements'][0]['height'],
            float)


class TestLocationFiltering(CollectorAPITestCase):
    def setUp(self):
        self.client.force_authenticate(self.collector_user)

    def test_that_measurements_can_be_retrieved_for_gauge_1(self):
        path = (BASE_PATH + 'gladstone-1/'
                '?start=2014-06-10T09:00:00Z&end=2014-06-10T11:00:00Z')
        data = decode_json(self.client.get(path).content)
        assert_equal(
            [
                {'datetime': '2014-06-10T10:00:00Z', 'height': 1.23},
                {'datetime': '2014-06-10T10:30:00Z', 'height': 1.56}
            ],
            data['raw_measurements'])

    def test_that_measurements_can_be_retrieved_for_gauge_2(self):
        path = (BASE_PATH + 'gladstone-2/'
                '?start=2014-06-10T09:00:00Z&end=2014-06-10T11:00:00Z')
        data = decode_json(self.client.get(path).content)
        assert_equal(
            [
                {'datetime': '2014-06-10T10:00:00Z', 'height': 5.67},
                {'datetime': '2014-06-10T10:30:00Z', 'height': 5.89}
            ],
            data['raw_measurements'])


class TestStartEndParameterFiltering(CollectorAPITestCase):
    def setUp(self):
        self.client.force_authenticate(self.collector_user)

    @staticmethod
    def _make_path(start_hour, start_min, end_hour, end_min):
        return (BASE_PATH + 'gladstone-1/'
                '?start=2014-06-10T{start_hour}:{start_min}:00Z'
                '&end=2014-06-10T{end_hour}:{end_min}:00Z').format(
                    start_hour=start_hour, start_min=start_min,
                    end_hour=end_hour, end_min=end_min)

    def test_that_start_filter_excludes_prior_datetimes(self):
        path = self._make_path(10, 1, 10, 5)
        data = decode_json(self.client.get(path).content)['raw_measurements']
        assert_equal([], data)

    def test_that_start_filter_includes_start_datetime(self):
        path = self._make_path(10, 0, 10, 5)
        data = decode_json(self.client.get(path).content)['raw_measurements']
        assert_equal([
            {
                'datetime': '2014-06-10T10:00:00Z',
                'height': 1.23
            }],
            data)

    def test_that_end_filter_excludes_end_datetime(self):
        path = self._make_path(9, 0, 10, 0)
        data = decode_json(self.client.get(path).content)['raw_measurements']
        assert_equal([], data)

    def test_that_end_filter_includes_previous_datetime(self):
        path = self._make_path(9, 0, 10, 1)
        data = decode_json(self.client.get(path).content)['raw_measurements']
        assert_equal([
            {
                'datetime': '2014-06-10T10:00:00Z',
                'height': 1.23
            }],
            data)

    def test_that_identical_start_and_end_gives_no_results(self):
        path = self._make_path(10, 0, 10, 0)
        data = decode_json(self.client.get(path).content)['raw_measurements']
        assert_equal([], data)

    def test_that_start_and_end_exactly_24_hours_is_ok_http_200(self):
        path = PATH + '?start=2014-06-10T00:00:00Z&end=2014-06-11T00:00:00Z'
        expected = {'raw_measurements': [
            {'datetime': '2014-06-10T10:00:00Z', 'height': 1.23},
            {'datetime': '2014-06-10T10:30:00Z', 'height': 1.56},
        ]}
        assert_json_response(self.client.get(path), 200, expected)


class TestStartEndResultsOrdering(APITestCase):
    pass
