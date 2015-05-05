import datetime
from nose.tools import assert_equal

import pytz
from api.apps.predictions.views.helpers import TideWindow
from api.apps.predictions.utils import create_tide_prediction

from api.apps.locations.models import Location


from django.test import TestCase

LIVERPOOL = None
SOUTHAMPTON = None
LIV_TIME_WINDOW = None
SOUTH_TIME_WINDOW = None

TIME_START = datetime.datetime(2015, 1, 1, 10, 0, tzinfo=pytz.UTC)
TIME_HW = datetime.datetime(2015, 1, 2, 10, 0, tzinfo=pytz.UTC)
TIME_END = datetime.datetime(2015, 1, 3, 10, 0, tzinfo=pytz.UTC)


def setUpModule():
    global LIVERPOOL, SOUTHAMPTON, LIV_TIME_WINDOW, SOUTH_TIME_WINDOW
    LIVERPOOL = Location.objects.create(slug='liverpool')
    SOUTHAMPTON = Location.objects.create(slug='southampton')

    LIV_TIME_WINDOW = TideWindow()
    LIV_TIME_WINDOW.start_prediction, LIV_TIME_WINDOW.end_prediction = (
        create_tide_prediction(LIVERPOOL, TIME_START, 1.0, False),
        create_tide_prediction(LIVERPOOL, TIME_END, 1.0, False)
    )
    LIV_TIME_WINDOW.high_tide_predictions = [
        create_tide_prediction(LIVERPOOL, TIME_HW, 5.0, False)
    ]

    SOUTH_TIME_WINDOW = TideWindow()
    SOUTH_TIME_WINDOW.start_prediction, SOUTH_TIME_WINDOW.end_prediction = (
        create_tide_prediction(SOUTHAMPTON, TIME_START, 1.0, False),
        create_tide_prediction(SOUTHAMPTON, TIME_HW, 5.0, False)
    )
    SOUTH_TIME_WINDOW.high_tide_predictions = [
        create_tide_prediction(SOUTHAMPTON, TIME_HW, 5.0, False)
    ]


def tearDownModule():
    LIVERPOOL.delete()
    SOUTHAMPTON.delete()


class TestTideWindow(TestCase):
    def test_truncate_end(self):
        LIV_TIME_WINDOW.truncate_end(TIME_HW)
        assert_equal(
            LIV_TIME_WINDOW.high_tide_prediction,
            LIV_TIME_WINDOW.end_prediction)

    def test_truncate_start(self):
        LIV_TIME_WINDOW.truncate_start(TIME_HW)
        assert_equal(
            LIV_TIME_WINDOW.high_tide_prediction,
            LIV_TIME_WINDOW.start_prediction)
