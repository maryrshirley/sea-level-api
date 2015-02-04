import datetime

from freezegun import freeze_time

from django.test import TestCase
from nose.tools import assert_equal


from api.apps.predictions.models import SurgePrediction

from api.apps.locations.models import Location

from api.apps.status.views.surge_predictions import (
    check_surge_predictions)

from api.apps.status.alert_manager import AlertType, disable_alert_until

from .helpers import (BASE_TIME, _make_good_surge_predictions,
                      _setup_locations, TestCheckBase)


class TestSurgePredictionsView(TestCase):
    BASE_PATH = '/1/_status/surge-predictions/'

    def _setup_all_ok(self):
        liverpool, southampton = _setup_locations()
        _make_good_surge_predictions()
        southampton.delete()  # so that it doesn't come up as a failure

    def _setup_not_ok(self):
        """
        Create two locations but with no data - this will cause a failure.
        """

        liverpool, southampton = _setup_locations()
        SurgePrediction.objects.all().delete()  # to ensure error

    def test_surge_predictions_page_has_status_ok_when_all_ok(self):
        self._setup_all_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'Surge Predictions: OK', status_code=200)

    def test_surge_predictions_page_has_status_error_when_not_ok(self):
        self._setup_not_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(
            response, 'Surge Predictions: ERROR', status_code=500)


class TestFunctionCheckSurgePredictions(TestCheckBase):
    @classmethod
    def setUpClass(self):
        _make_good_surge_predictions()

    @classmethod
    def tearDownClass(self):
        Location.objects.all().delete()
        SurgePrediction.objects.all().delete()

    def test_that_surge_predictions_for_next_36_hours_every_minute_is_ok(self):
        with freeze_time(BASE_TIME):
            (ok, text) = check_surge_predictions(self.liverpool)

        assert_equal('OK', text)
        assert_equal(True, ok)

    def _make_bad_surge_location(self):
        prediction = SurgePrediction.objects.get(
            location=self.liverpool,
            minute__datetime=BASE_TIME + datetime.timedelta(minutes=10))
        prediction.delete()

    def test_that_a_missing_surge_prediction_in_next_36_hours_not_ok(self):
        self._make_bad_surge_location()
        with freeze_time(BASE_TIME):
            (ok, text) = check_surge_predictions(self.liverpool)

        assert_equal(False, ok)
        assert_equal('Missing data for next 36 hours: 2159 vs 2160', text)

    def test_that_surge_prediction_alerts_can_be_disabled(self):
        self._make_bad_surge_location()

        with freeze_time(BASE_TIME):
            disable_alert_until(self.liverpool, AlertType.surge_predictions,
                                BASE_TIME + datetime.timedelta(hours=1))
            (ok, text) = check_surge_predictions(self.liverpool)

        assert_equal(True, ok)
        assert_equal('OK (alert disabled)', text)

    def test_that_predictions_for_liverpool_dont_affect_southampton(self):
        with freeze_time(BASE_TIME):
            (ok, text) = check_surge_predictions(self.southampton)

        assert_equal(False, ok)
