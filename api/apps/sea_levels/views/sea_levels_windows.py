from django.http import Http404
from rest_framework.generics import ListAPIView

from api.libs.param_parsers import parse_time_range, parse_sea_level

from ..models import CombinedPredictionObservation
from ..serializers.sea_level_windows import SeaLevelWindowsSerializer


class SeaLevelsWindows(ListAPIView):

    serializer_class = SeaLevelWindowsSerializer

    def get_location_slug(self):
        location_slug = self.kwargs.get('location_slug', None)
        if not location_slug:
            raise Http404

        return location_slug

    def get_sea_level(self):
        return parse_sea_level(self.request.query_params.get('sea_level'))

    def get_queryset(self, *args, **kwargs):
        query_params = self.request.query_params

        time_range = parse_time_range(
            query_params.get('start', None),
            query_params.get('end', None)
        )

        return CombinedPredictionObservation.objects. \
            sea_level_windows(self.get_location_slug(),
                              self.get_sea_level(),
                              time_range.start,
                              time_range.end)


class SeaLevelWindowsNow(SeaLevelsWindows):

    serializer_class = SeaLevelWindowsSerializer

    def get_queryset(self, *args, **kwargs):
        return CombinedPredictionObservation.objects. \
            sea_level_windows_now(self.get_location_slug(),
                                  self.get_sea_level())
