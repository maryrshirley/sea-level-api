import datetime

from freezegun import freeze_time

from django.test import TestCase
from nose.tools import assert_equal


from api.apps.observations.models import Observation
from api.apps.observations.utils import create_observation
from api.apps.predictions.models import TidePrediction, SurgePrediction
from api.apps.predictions.utils import create_tide_prediction

from api.apps.locations.models import Location

from api.apps.status.views.status_index import check_observations

from api.apps.status.alert_manager import AlertType, disable_alert_until


from .helpers import (BASE_TIME, _make_good_surge_predictions,
                      _setup_locations, TestCheckBase)


class TestStatusIndexView(TestCase):
    BASE_PATH = '/1/_status/'

    def _setup_all_ok(self):
        liverpool, southampton = _setup_locations()

        create_tide_prediction(
            liverpool,
            BASE_TIME + datetime.timedelta(days=31),
            5.0)
        _make_good_surge_predictions()
        create_observation(
            liverpool,
            BASE_TIME - datetime.timedelta(minutes=10),
            4.5,
            True)
        southampton.delete()  # so that it doesn't come up as a failure

    def _setup_not_ok(self):
        """
        Create two locations but with no data - this will cause a failure.
        """

        liverpool, southampton = _setup_locations()
        TidePrediction.objects.all().delete()
        SurgePrediction.objects.all().delete()
        Observation.objects.all().delete()

    def test_that_status_page_has_api_status_ok_when_all_ok(self):
        self._setup_all_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'API Status: OK', status_code=200)

    def test_that_status_page_has_api_status_error_when_something_not_ok(self):
        self._setup_not_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'API Status: ERROR', status_code=500)


class TestCheckObservations(TestCheckBase):
    OK_MINUTES = 120

    def test_that_observations_more_recent_than_one_hour_are_ok(self):
        create_observation(
            self.liverpool,
            BASE_TIME - datetime.timedelta(minutes=self.OK_MINUTES - 1),
            10.0, True)

        with freeze_time(BASE_TIME):
            (ok, text) = check_observations(self.liverpool)

        assert_equal(True, ok)
        assert_equal('OK', text)

    def _make_bad_observations(self):
        create_observation(
            self.liverpool,
            BASE_TIME - datetime.timedelta(minutes=self.OK_MINUTES + 1),
            10.0, True)

    def test_that_observations_over_two_hours_old_not_ok(self):
        self._make_bad_observations()

        with freeze_time(BASE_TIME):
            (ok, text) = check_observations(self.liverpool)

        assert_equal(False, ok)
        assert_equal('> 2 hours old', text)

    def test_that_observations_alerts_can_be_disabled(self):
        self._make_bad_observations()

        with freeze_time(BASE_TIME):
            disable_alert_until(self.liverpool, AlertType.observations,
                                BASE_TIME + datetime.timedelta(hours=1))
            (ok, text) = check_observations(self.liverpool)

        assert_equal(True, ok)
        assert_equal('OK (alert disabled)', text)

    def test_that_observations_from_liverpool_dont_affect_southampton(self):
        create_observation(
            self.liverpool,
            BASE_TIME - datetime.timedelta(minutes=self.OK_MINUTES - 1),
            10.0, True)

        with freeze_time(BASE_TIME):
            (ok, text) = check_observations(self.southampton)

        assert_equal(False, ok)
        assert_equal('> 2 hours old', text)
