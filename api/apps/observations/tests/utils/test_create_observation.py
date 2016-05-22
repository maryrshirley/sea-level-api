import datetime
import pytz

from django.test import TestCase
from nose.tools import assert_equal

from api.apps.observations.models import Observation
from api.apps.observations.utils import create_observation
from api.libs.minute_in_time.models import Minute
from api.libs.test_utils.location import LocationMixin


class TestCreateObservation(TestCase, LocationMixin):

    def setUp(self):
        super(TestCreateObservation, self).setUp()
        Minute.objects.all().delete()
        self.datetime = datetime.datetime(
            2014, 3, 5, 17, 45, tzinfo=pytz.UTC)
        self.liverpool = self.create_location(slug='liverpool')

    def tearDown(self):
        self.liverpool.delete()
        super(TestCreateObservation, self).tearDown()

    def test_that_observation_can_be_created_when_minute_already_exists(self):
        Minute.objects.create(datetime=self.datetime)
        create_observation(self.liverpool, self.datetime, 123.45, False)
        assert_equal(123.45, Observation.objects.get().sea_level)

    def test_that_observation_can_be_created_when_minute_doesnt_exist(self):
        create_observation(self.liverpool, self.datetime, 123.45, False)
        assert_equal(123.45, Observation.objects.get().sea_level)

    def test_that_observation_can_be_updated_when_minute_already_exists(self):
        Minute.objects.create(datetime=self.datetime)

        create_observation(self.liverpool, self.datetime, 123.45, False)
        create_observation(self.liverpool, self.datetime, 45.67, False)

        assert_equal(45.67, Observation.objects.get().sea_level)

    def test_that_observation_can_be_updated_when_minute_doesnt_exist(self):
        create_observation(self.liverpool, self.datetime, 123.45, False)
        create_observation(self.liverpool, self.datetime, 45.67, False)

        assert_equal(45.67, Observation.objects.get().sea_level)
