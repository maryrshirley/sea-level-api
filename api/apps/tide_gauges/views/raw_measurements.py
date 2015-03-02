from rest_framework.generics import CreateAPIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from ..serializers import RawMeasurementSerializer
from ..models import RawMeasurement, TideGauge

import functools


class RawMeasurements(CreateAPIView):
    """
    Save raw measurements for a tide gauge. Measurements must be given in a
    JSON array.

    - Any measurements which already exist will be updated.
    - The endpoint returns HTTP 201 CREATED regardless of whether the record
      was created or updated.

    Note that an invalid record in the list will cause the entire batch to be
    dropped.
    """

    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = RawMeasurement.objects.none()  # req for DjangoModelPermissions

    # I prefer not to override `get_serializer()` just to pass in `many=True`.
    # There may be a better way than using `partial` though.
    # See http://stackoverflow.com/q/28814806/2920176
    serializer_class = functools.partial(RawMeasurementSerializer, many=True)

    def get_serializer_context(self, *args, **kwargs):
        # Augment the default context (containing response etc) with the tide
        # gauge instance referred to by the slug in the request URL.
        # This allows access to the serializer so it can create and query
        # RawMeasurement models.

        c = super(CreateAPIView, self).get_serializer_context(*args, **kwargs)
        tide_gauge = TideGauge.objects.get(slug=self.kwargs['tide_gauge_slug'])

        def combine_dicts(a, b):
            return dict(list(a.items()) + list(b.items()))

        return combine_dicts(c, {'tide_gauge': tide_gauge})
