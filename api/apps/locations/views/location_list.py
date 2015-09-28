from rest_framework.generics import ListAPIView

from api.apps.locations.serializers import LocationSerializer

from api.libs.json_envelope_renderer import replace_json_renderer

from .get_queryset import get_queryset


class LocationList(ListAPIView):
    """
    List all locations at which there may be sea level predictions.
    """
    renderer_classes = replace_json_renderer(ListAPIView.renderer_classes)

    serializer_class = LocationSerializer

    def get_queryset(self, *args, **kwargs):
        return get_queryset(user=self.request.user)
