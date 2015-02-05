import datetime

from freezegun import freeze_time

from django.test import TestCase
from nose.tools import assert_equal

from api.apps.observations.utils import create_observation
from api.apps.observations.models import Observation


from api.apps.status.views.observations import check_observations

from api.apps.status.alert_manager import AlertType, disable_alert_until

from .helpers import (BASE_TIME, _setup_locations, TestCheckBase)


class TestObservationsView(TestCase):
    BASE_PATH = '/1/_status/observations/liverpool/'

    def _setup_all_ok(self):
        liverpool, southampton = _setup_locations()
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
        Observation.objects.all().delete()  # to ensure error

    def test_observations_page_has_status_ok_when_all_ok(self):
        self._setup_all_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'Observations: OK', status_code=200)

    def test_observations_page_has_status_error_when_not_ok(self):
        self._setup_not_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(
            response, 'Observations: ERROR', status_code=500)


class TestFunctionCheckObservations(TestCheckBase):
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
