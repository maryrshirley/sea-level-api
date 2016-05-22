import datetime
import pytz


from django.test import TestCase


from api.apps.predictions.models import TidePrediction, SurgePrediction
from api.apps.predictions.utils import create_surge_prediction
from api.libs.test_utils.location import LocationMixin


BASE_TIME = datetime.datetime(2014, 8, 1, 10, 0, 0, tzinfo=pytz.UTC)


def _make_good_surge_predictions(liverpool):

    for minute in range((36 * 60) + 10):
        create_surge_prediction(
            liverpool,
            BASE_TIME + datetime.timedelta(minutes=minute),
            0.2)


class TestCheckBase(TestCase, LocationMixin):

    def setUp(self):
        super(TestCheckBase, self).setUp()
        self.liverpool = self.create_location()
        self.southampton = self.create_location(self.LOCATION_B)

    def tearDown(self):
        TidePrediction.objects.all().delete()
        SurgePrediction.objects.all().delete()
        if self.liverpool.id is not None:
            self.liverpool.delete()
        if self.southampton.id is not None:
            self.southampton.delete()
        super(TestCheckBase, self).tearDown()
