from rest_framework.generics import ListAPIView

from api.libs.json_envelope_renderer import replace_json_renderer
from api.libs.param_parsers import (parse_location, parse_time_range,
                                    parse_interval)

from ..models import CombinedPredictionObservation
from ..serializers import SeaLevelSerializer


class SeaLevels(ListAPIView):
    """
    Get tidal predictions at a given location. Valid parameters are
    `start` and `end` (in format `2014-05-01T00:17:00Z`) and `interval` in
    minutes.
    """
    renderer_classes = replace_json_renderer(ListAPIView.renderer_classes)
    serializer_class = SeaLevelSerializer

    def get_queryset(self, query_params=None, *args, **kwargs):
        if query_params is None:
            query_params = self.request.query_params

        interval_mins = parse_interval(query_params.get('interval', '1'))
        location = parse_location(self.kwargs.get('location_slug', None))
        time_range = parse_time_range(
            query_params.get('start', None),
            query_params.get('end', None))

        # limit to 24 hours of data
        return get_queryset(location, time_range)[:24 * 60:interval_mins]


def get_queryset(location, time_range):
    queryset = CombinedPredictionObservation.objects.filter(
        location=location,
        datetime__gte=time_range.start,
        datetime__lt=time_range.end)

    return queryset.order_by('datetime')
