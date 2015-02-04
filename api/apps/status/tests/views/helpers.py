import datetime
import pytz


from django.test import TestCase


from api.apps.predictions.models import TidePrediction, SurgePrediction
from api.apps.predictions.utils import create_surge_prediction

from api.apps.locations.models import Location


BASE_TIME = datetime.datetime(2014, 8, 1, 10, 0, 0, tzinfo=pytz.UTC)


def _make_good_surge_predictions():
    liverpool, _ = _setup_locations()

    for minute in range((36 * 60) + 10):
        create_surge_prediction(
            liverpool,
            BASE_TIME + datetime.timedelta(minutes=minute),
            0.2)


def _setup_locations():
    liverpool, _ = Location.objects.get_or_create(
        slug='liverpool', name='Liverpool')
    southampton, _ = Location.objects.get_or_create(
        slug='southampton', name='Southampton')
    return liverpool, southampton


class TestCheckBase(TestCase):
    def setUp(self):
        self.liverpool, self.southampton = _setup_locations()

    def tearDown(self):
        Location.objects.all().delete()
        TidePrediction.objects.all().delete()
        SurgePrediction.objects.all().delete()
