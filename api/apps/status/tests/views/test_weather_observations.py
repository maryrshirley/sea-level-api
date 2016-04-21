from django.test import TestCase

from nose.tools import assert_equal

from api.apps.observations.models import WeatherObservation
from api.libs.test_utils.datetime_utils import delta
from api.libs.test_utils.mixins import LocationMixin
from api.libs.test_utils.weather import CreateObservationMixin


class TestWeatherObservationsView(TestCase, CreateObservationMixin,
                                  LocationMixin):

    endpoint = '/1/_status/weather-observations/'

    def setUp(self):
        super(TestWeatherObservationsView, self).setUp()
        self.setUpLocation()

    def tearDown(self):
        self.tearDownLocation()
        super(TestWeatherObservationsView, self).tearDown()

    def test_that_endpoint_exists(self):
        response = self.client.options(self.endpoint)
        assert_equal(200, response.status_code)

    def test_that_http_options_allowed(self):
        response = self.client.options(self.endpoint)
        assert_equal(200, response.status_code)
        assert_equal('GET, HEAD, OPTIONS', response['Allow'])

    def assert_status(self, ok, text, location):
        status = WeatherObservation.objects.status(location)
        assert_equal(ok, status.ok)
        assert_equal(text, status.text)

    def test_that_weather_observation_has_status(self):
        observation = self.create_observation_now()
        self.assert_status(True, "OK", self.location)
        observation.delete()

    def test_that_no_observation_has_missing_status(self):
        self.assert_status(False, "Missing data for the previous 24 hours",
                           self.location)

    def test_that_old_observation_has_missing_status(self):
        observation = self.create_observation(datetime=delta(days=-2))
        self.assert_status(False, "Missing data for the previous 24 hours",
                           self.location)
        observation.delete()

    def test_that_no_location_has_invalid_status(self):
        self.assert_status(False, "Invalid location", None)
