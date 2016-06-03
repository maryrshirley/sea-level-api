from collections import namedtuple
from datetime import timedelta
from itertools import tee
import logging

ONE_DAY = timedelta(hours=24)
ONE_MIN = timedelta(seconds=60)

TimeRange = namedtuple('TimeRange', 'start,end')

logger = logging.getLogger(__name__)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def transform_time_window(time_range, extended_time_range, window):
    if not window.is_inside_time_range(time_range):
        return None

    if window.extends_after(extended_time_range.end):
        window.truncate_end(time_range.end)

    if window.extends_before(extended_time_range.start):
        window.truncate_start(time_range.start)

    if window.validate():
        return window


class PredictionWindow(object):
    def __init__(self, model):
        self.start_prediction = None
        self.end_prediction = None
        self.high_tide_predictions = []
        self.model = model

    def validate(self):
        if not self.high_tide_predictions:
            logger.info('PredictionWindow invalid: no high tide predictions')
            return False

        if self.start_prediction is None:
            logger.info('PredictionWindow invalid: no start prediction')
            return False

        if self.end_prediction is None:
            logger.info('PredictionWindow invalid: no end prediction')
            return False

        if (self.high_tide_prediction.datetime <
                self.start_prediction.datetime):
            logger.info('PredictionWindow invalid: high tide before start')
            return False

        if (self.high_tide_prediction.datetime >
                self.end_prediction.datetime):
            logger.info('PredictionWindow invalid: high tide after end')
            return False

        return True

    def spawn_for_each_high_tide(self):
        for high_tide_prediction in self.high_tide_predictions:
            t = PredictionWindow(self.model)
            t.start_prediction = self.start_prediction
            t.end_prediction = self.end_prediction
            t.high_tide_prediction = high_tide_prediction
            yield t

    def add_prediction(self, prediction):
        if self.start_prediction is None:
            self.start_prediction = prediction
        else:
            self.end_prediction = prediction

        if prediction.predicted_is_high:
            self.high_tide_predictions.append(prediction)

    @property
    def high_tide_prediction(self):
        assert len(self.high_tide_predictions) == 1
        return self.high_tide_predictions[0]

    @high_tide_prediction.setter
    def high_tide_prediction(self, prediction):
        self.high_tide_predictions = [prediction]

    def is_inside_time_range(self, time_range):
        """
        Return True if the self is fully or partially inside the given time
        range
                          start          end
                            |             |
                  <--F--> <--T--> <-T->  <--T-->  <--F-->

        where first <------> last
        """
        return (self.start_prediction.datetime <= time_range.end and
                self.end_prediction.datetime >= time_range.start)

    def truncate_end(self, to_datetime):
        self.end_prediction = self.model.objects.get(
            location=self.start_prediction.location,
            datetime=to_datetime)

    def truncate_start(self, to_datetime):
        self.start_prediction = self.model.objects.get(
            location=self.start_prediction.location,
            datetime=to_datetime)

    def extends_after(self, when):
        return (self.end_prediction.datetime >=
                when - timedelta(minutes=1))  # TODO ratty?

    def extends_before(self, when):
        return self.start_prediction.datetime <= when
