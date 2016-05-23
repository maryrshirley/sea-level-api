import datetime
from nose.tools import assert_equal

import pytz
from api.apps.predictions.views.helpers import TideWindow
from api.apps.predictions.utils import create_tide_prediction

from api.libs.test_utils.location import LocationMixin


from django.test import TestCase

TIME_START = datetime.datetime(2015, 1, 1, 10, 0, tzinfo=pytz.UTC)
TIME_HW = datetime.datetime(2015, 1, 2, 10, 0, tzinfo=pytz.UTC)
TIME_END = datetime.datetime(2015, 1, 3, 10, 0, tzinfo=pytz.UTC)


class TestTideWindow(TestCase, LocationMixin):

    @classmethod
    def setUpClass(cls):
        cls.liverpool = cls.create_location(slug='liverpool', name='Liverpool')
        cls.southampton = cls.create_location(slug='southampton',
                                              name='Southampton')

        liv_time_window = TideWindow()
        liv_time_window.start_prediction, liv_time_window.end_prediction = (
            create_tide_prediction(cls.liverpool, TIME_START, 1.0, False),
            create_tide_prediction(cls.liverpool, TIME_END, 1.0, False)
        )
        liv_time_window.high_tide_predictions = [
            create_tide_prediction(cls.liverpool, TIME_HW, 5.0, False)
        ]
        cls.liv_time_window = liv_time_window

        south_time_window = TideWindow()
        start_prediction, end_prediction = (
            create_tide_prediction(cls.southampton, TIME_START, 1.0, False),
            create_tide_prediction(cls.southampton, TIME_HW, 5.0, False)
        )
        south_time_window.start_prediction = start_prediction
        south_time_window.end_prediction = end_prediction
        south_time_window.high_tide_predictions = [
            create_tide_prediction(cls.southampton, TIME_HW, 5.0, False)
        ]
        cls.south_time_window = south_time_window

    @classmethod
    def tearDownClass(cls):
        cls.liverpool.delete()
        cls.southampton.delete()

    def test_truncate_end(self):
        self.liv_time_window.truncate_end(TIME_HW)
        assert_equal(
            self.liv_time_window.high_tide_prediction,
            self.liv_time_window.end_prediction)

    def test_truncate_start(self):
        self.liv_time_window.truncate_start(TIME_HW)
        assert_equal(
            self.liv_time_window.high_tide_prediction,
            self.liv_time_window.start_prediction)
