from rest_framework.generics import ListAPIView

from api.libs.json_envelope_renderer import replace_json_renderer
from api.libs.param_parsers import (
    parse_interval, parse_location, parse_time_range)
from api.libs.user_permissions.permissions_classes import (
    AllowUserSpecificAccess,)

from ..serializers import TideLevelSerializer

from .helpers import get_queryset


class TideLevels(ListAPIView):
    """
    Get tidal predictions at a given location. Valid parameters are
    `start` and `end` (in format `2014-05-01T00:17:00Z`) and `interval` in
    minutes.
    """
    renderer_classes = replace_json_renderer(ListAPIView.renderer_classes)
    serializer_class = TideLevelSerializer
    permission_classes = (AllowUserSpecificAccess,)

    def get_queryset(self, query_params=None, *args, **kwargs):
        if query_params is None:
            query_params = self.request.query_params

        interval_mins = parse_interval(query_params.get('interval', '1'))
        location = parse_location(self.kwargs.get('location_slug', None))

        self.check_object_permissions(self.request, location)

        time_range = parse_time_range(
            query_params.get('start', None),
            query_params.get('end', None)
        )

        # limit to 24 hours of data
        return get_queryset(location, time_range)[:24 * 60:interval_mins]
