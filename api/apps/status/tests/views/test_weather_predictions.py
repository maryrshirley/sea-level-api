from django.test import TestCase
from freezegun import freeze_time

from nose.tools import assert_equal

from api.apps.predictions.models import WeatherPrediction
from api.apps.status.alert_manager import AlertType, disable_alert_until
from api.libs.test_utils.datetime_utils import delta
from api.libs.test_utils.mixins import LocationMixin
from api.libs.test_utils.weather import CreatePredictionMixin
from api.libs.view_helpers import now_rounded


class TestWeatherPredictionsView(TestCase, CreatePredictionMixin,
                                 LocationMixin):

    endpoint = '/1/_status/weather-predictions/'

    def setUp(self):
        super(TestWeatherPredictionsView, self).setUp()
        self.setUpLocation()

    def tearDown(self):
        self.tearDownLocation()
        super(TestWeatherPredictionsView, self).tearDown()

    def test_that_endpoint_exists(self):
        response = self.client.options(self.endpoint)
        assert_equal(200, response.status_code)

    def test_that_http_options_allowed(self):
        response = self.client.options(self.endpoint)
        assert_equal(200, response.status_code)
        assert_equal('GET, HEAD, OPTIONS', response['Allow'])

    def assert_status(self, ok, text, location):
        status = WeatherPrediction.objects.status(location)
        assert_equal(ok, status.ok)
        assert_equal(text, status.text)

    def test_that_weather_prediction_has_status(self):
        prediction = self.create_prediction_now()
        self.assert_status(True, "OK", self.location)
        prediction.delete()

    def test_that_no_prediction_has_missing_status(self):
        self.assert_status(False, "Missing data for the next 24 hours",
                           self.location)

    def test_that_old_prediction_has_missing_status(self):
        prediction = self.create_prediction(valid_from=delta(days=-2),
                                            valid_to=delta(days=-1))
        self.assert_status(False, "Missing data for the next 24 hours",
                           self.location)
        prediction.delete()

    def test_that_no_location_has_invalid_status(self):
        self.assert_status(False, "Invalid location", None)

    def test_that_weather_observations_alerts_can_be_disabled(self):
        now = now_rounded()
        with freeze_time(now):
            disable_alert_until(self.location, AlertType.weather_predictions,
                                delta(hours=1))
            self.assert_status(True, 'OK (alert disabled)', self.location)
