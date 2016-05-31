import datetime

import pytz
from nose.tools import assert_equal
from freezegun import freeze_time
from django.test import TestCase

from api.apps.status.alert_manager import (
    AlertType, disable_alert_until)

from api.apps.status.models import LocationStatusConfig
from api.libs.test_utils.location import LocationMixin


BASE_DATE = datetime.datetime(2014, 11, 24, 10, 0, tzinfo=pytz.UTC)


class TestDisabledAlerts(TestCase, LocationMixin):
    def setUp(self):
        super(TestDisabledAlerts, self).setUp()
        self.liverpool = self.create_location()
        self.config = LocationStatusConfig.objects.create(
            location=self.liverpool)

    def tearDown(self):
        LocationStatusConfig.objects.all().delete()
        self.liverpool.delete()
        super(TestDisabledAlerts, self).tearDown()

    def _disable(self, alert_type):
        disable_alert_until(self.liverpool, alert_type,
                            BASE_DATE + datetime.timedelta(hours=10))

    def test_that_disabled_alerts_is_empty_with_no_disabled_alerts(self):
        assert_equal('', self.config.disabled_alerts())

    def test_tide_predictions_disabled_alert_string(self):
        with freeze_time(BASE_DATE):
            self._disable(AlertType.tide_predictions)
            assert_equal('tide_predictions', self.config.disabled_alerts())

    def test_surge_predictions_disabled_alert_string(self):
        with freeze_time(BASE_DATE):
            self._disable(AlertType.surge_predictions)
            assert_equal('surge_predictions', self.config.disabled_alerts())

    def test_observations_disabled_alert_string(self):
        with freeze_time(BASE_DATE):
            self._disable(AlertType.observations)
            assert_equal('observations', self.config.disabled_alerts())

    def test_tide_and_surge_disabled_alert_string(self):
        with freeze_time(BASE_DATE):
            self._disable(AlertType.tide_predictions)
            self._disable(AlertType.surge_predictions)
            assert_equal('surge_predictions, tide_predictions',
                         self.config.disabled_alerts())

    def test_schedule_disabled_alert_string(self):
        with freeze_time(BASE_DATE):
            self._disable(AlertType.schedule)
            assert_equal('schedule',
                         self.config.disabled_alerts())
