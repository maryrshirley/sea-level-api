from django.test import TestCase

from freezegun import freeze_time
from nose.tools import assert_equal

from api.apps.status.alert_manager import AlertType, disable_alert_until
from api.libs.test_utils.datetime_utils import delta
from api.libs.test_utils.schedule import ScheduleMixin
from api.libs.view_helpers import now_rounded


class TestScheduleView(TestCase, ScheduleMixin):

    def setUp(self):
        super(TestScheduleView, self).setUp()
        self.setUpScheduleRequirements()

    def tearDown(self):
        self.tearDownScheduleRequirements()
        super(TestScheduleView, self).tearDown()

    def test_that_http_options_allowed(self):
        response = self.client.options(self.schedule_status_endpoint)
        assert_equal(200, response.status_code)
        assert_equal('GET, HEAD, OPTIONS', response['Allow'])

    def assert_status(self, ok, text, location):
        status = self.Schedule.objects.status(location)
        assert_equal(ok, status.ok)
        assert_equal(text, status.text)

    def test_that_schedule_has_status(self):
        schedule = self.create_schedule()
        with freeze_time(schedule.departure.datetime):
            self.assert_status(True, "OK", self.origin)
        schedule.delete()

    def test_that_no_schedule_has_missing_status(self):
        self.assert_status(False, "Missing data for the next 24 hours",
                           self.origin)

    def test_that_old_schedule_has_missing_status(self):
        schedule = self.create_schedule()
        self.assert_status(False, "Missing data for the next 24 hours",
                           self.origin)
        schedule.delete()

    def test_that_no_location_has_invalid_status(self):
        self.assert_status(False, "Invalid location", None)

    def test_that_schedule_alerts_can_be_disabled(self):
        now = now_rounded()
        with freeze_time(now):
            disable_alert_until(self.origin, AlertType.schedule,
                                delta(hours=1))
            self.assert_status(True, 'OK (alert disabled)', self.origin)
