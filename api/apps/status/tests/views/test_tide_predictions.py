import datetime

from freezegun import freeze_time

from nose.tools import assert_equal

from api.apps.predictions.utils import create_tide_prediction
from api.apps.predictions.models import SurgePrediction

from api.apps.status.views.tide_predictions import (
    check_tide_predictions)

from api.apps.status.alert_manager import AlertType, disable_alert_until

from .helpers import (BASE_TIME, TestCheckBase)


class TestTidePredictionsView(TestCheckBase):
    BASE_PATH = '/1/_status/tide-predictions/'

    def _setup_tide_ok(self):
        create_tide_prediction(
            self.liverpool,
            BASE_TIME + datetime.timedelta(days=31),
            5.0)
        self.southampton.delete()  # so that it doesn't come up as a failure

    @staticmethod
    def _setup_tide_not_ok():
        """
        Create two locations but with no data - this will cause a failure.
        """

        SurgePrediction.objects.all().delete()  # to ensure error

    def test_tide_predictions_page_has_status_ok_when_all_ok(self):
        self._setup_tide_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'Tide Predictions: OK', status_code=200)

    def test_tide_predictions_page_has_status_error_when_not_ok(self):
        self._setup_tide_not_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(
            response, 'Tide Predictions: ERROR', status_code=500)


class TestFunctionCheckTidePredictions(TestCheckBase):
    def test_that_tide_predictions_further_than_one_month_is_ok(self):
        create_tide_prediction(
            self.liverpool,
            BASE_TIME + datetime.timedelta(days=31),
            10.0)

        with freeze_time(BASE_TIME):
            (ok, text) = check_tide_predictions(self.liverpool)

        assert_equal(True, ok)
        assert_equal('OK', text)

    def _make_bad_tide_location(self):
        create_tide_prediction(
            self.liverpool,
            BASE_TIME + datetime.timedelta(days=29),
            10.0)

    def test_that_tide_predictions_less_than_one_month_not_ok(self):
        self._make_bad_tide_location()

        with freeze_time(BASE_TIME):
            (ok, text) = check_tide_predictions(self.liverpool)

        assert_equal(False, ok)
        assert_equal('< 30 days left', text)

    def test_that_tide_prediction_alerts_can_be_disabled(self):
        self._make_bad_tide_location()

        with freeze_time(BASE_TIME):
            disable_alert_until(self.liverpool, AlertType.tide_predictions,
                                BASE_TIME + datetime.timedelta(hours=1))
            (ok, text) = check_tide_predictions(self.liverpool)

        assert_equal(True, ok)
        assert_equal('OK (alert disabled)', text)

    def test_that_predictions_for_liverpool_dont_affect_southampton(self):
        create_tide_prediction(
            self.liverpool,
            BASE_TIME + datetime.timedelta(days=31),
            10.0)

        with freeze_time(BASE_TIME):
            (ok, text) = check_tide_predictions(self.southampton)

        assert_equal(False, ok)
        assert_equal('< 30 days left', text)
