from .sea_levels import SeaLevels

from api.libs.param_parsers import parse_location

from ..models import CombinedPredictionObservation


class SeaLevelsLatest(SeaLevels):

    def get_queryset(self, query_params=None, *args, **kwargs):
        location = parse_location(self.kwargs.get('location_slug', None))
        return CombinedPredictionObservation.objects.latest_object(location)
