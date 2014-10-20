import datetime

from functools import partial

try:
    # Python 2: use iterator versions
    from itertools import imap as map
    from itertools import ifilter as filter
except ImportError:
    pass

from rest_framework.generics import ListAPIView

from api.libs.json_envelope_renderer import replace_json_renderer
from api.libs.param_parsers import (parse_location, parse_time_range,
                                    parse_tide_level)

from ..models import TidePrediction
from ..serializers import TideWindowSerializer

from .helpers import (get_queryset, split_prediction_windows, TimeRange)


ONE_DAY = datetime.timedelta(hours=24)


class TideWindows(ListAPIView):
    """
    Get time windows where the tide prediction is above a given height.
    Valid parameters are `start` and `end` (in format `2014-05-01T00:17:00Z`)
    and `tide_level` in metres.
    """
    renderer_classes = replace_json_renderer(ListAPIView.renderer_classes)
    serializer_class = TideWindowSerializer

    def get_queryset(self, query_params=None, *args, **kwargs):
        if query_params is None:
            query_params = self.request.query_params

        location = parse_location(self.kwargs.get('location_slug', None))
        time_range = parse_time_range(
            query_params.get('start', None),
            query_params.get('end', None)
        )

        min_tide_level = parse_tide_level(
            self.request.query_params.get('tide_level'))

        extended_time_range = TimeRange(
            start=time_range.start - ONE_DAY,
            end=time_range.end + ONE_DAY)

        predictions = get_queryset(location, extended_time_range).filter(
            tide_level__gte=min_tide_level)

        return filter(None, map(
            partial(transform_time_window, time_range, extended_time_range),
            make_tide_time_windows(predictions)))


class TimeWindow(object):
    def __init__(self, start_prediction, end_prediction):

        self.start_prediction = start_prediction
        self.end_prediction = end_prediction

    def is_inside_time_range(self, time_range):
        """
        Return True if the self is fully or partially inside the given time
        range
                          start          end
                            |             |
                  <--F--> <--T--> <-T->  <--T-->  <--F-->

        where first <------> last
        """
        return (self.start_prediction.minute.datetime <= time_range.end
                and self.end_prediction.minute.datetime >= time_range.start)

    def truncate_end(self, to_datetime):
        self.end_prediction = TidePrediction.objects.get(
            minute__datetime=to_datetime)

    def truncate_start(self, to_datetime):
        self.start_prediction = TidePrediction.objects.get(
            minute__datetime=to_datetime)

    def extends_after(self, when):
        return (self.end_prediction.minute.datetime
                >= when - datetime.timedelta(minutes=1))  # TODO ratty?

    def extends_before(self, when):
        return self.start_prediction.minute.datetime <= when


def make_tide_time_windows(all_predictions_above_threshold):
    for start, end in split_prediction_windows(
            all_predictions_above_threshold):
        yield TimeWindow(
            start_prediction=start,
            end_prediction=end
        )


def transform_time_window(time_range, extended_time_range, window):
    if not window.is_inside_time_range(time_range):
        return None

    if window.extends_after(extended_time_range.end):
        window.truncate_end(time_range.end)

    if window.extends_before(extended_time_range.start):
        window.truncate_start(time_range.start)

    return window
