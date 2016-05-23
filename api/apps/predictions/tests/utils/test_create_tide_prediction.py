import datetime
import pytz

from django.test import TestCase
from nose.tools import assert_equal

from api.apps.predictions.models import TidePrediction
from api.apps.predictions.utils import create_tide_prediction
from api.libs.minute_in_time.models import Minute
from api.libs.test_utils.location import LocationMixin


class TestCreateTidePrediction(TestCase, LocationMixin):

    @classmethod
    def setUpClass(cls):
        super(TestCreateTidePrediction, cls).setUpClass()
        Minute.objects.all().delete()
        cls.datetime = datetime.datetime(
            2014, 3, 5, 17, 45, tzinfo=pytz.UTC)
        cls.liverpool = cls.create_location()

    @classmethod
    def tearDownClass(cls):
        cls.liverpool.delete()
        super(TestCreateTidePrediction, cls).tearDownClass()

    def test_that_prediction_can_be_created_when_minute_already_exists(self):
        Minute.objects.create(datetime=self.datetime)
        create_tide_prediction(self.liverpool, self.datetime, 123.45)
        assert_equal(123.45, TidePrediction.objects.get().tide_level)

    def test_that_prediction_can_be_created_when_minute_doesnt_exist(self):
        create_tide_prediction(self.liverpool, self.datetime, 123.45)
        assert_equal(123.45, TidePrediction.objects.get().tide_level)

    def test_that_prediction_can_be_updated_when_minute_already_exists(self):
        Minute.objects.create(datetime=self.datetime)

        create_tide_prediction(self.liverpool, self.datetime, 123.45)
        create_tide_prediction(self.liverpool, self.datetime, 45.67)

        assert_equal(45.67, TidePrediction.objects.get().tide_level)

    def test_that_prediction_can_be_updated_when_minute_doesnt_exist(self):
        create_tide_prediction(self.liverpool, self.datetime, 123.45)
        create_tide_prediction(self.liverpool, self.datetime, 45.67)

        assert_equal(45.67, TidePrediction.objects.get().tide_level)
