import datetime

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import ListCreateAPIView

from api.libs.param_parsers import (parse_time_range, MissingParameterError,
                                    ObjectNotFoundError, TimeRangeError)

from api.libs.json_envelope_renderer import replace_json_renderer
from api.libs.user_permissions.permissions_classes import (
    AllowInternalCollectorsReadAndWrite)

from ..serializers import RawMeasurementSerializer
from ..models import RawMeasurement, TideGauge

import functools


class RawMeasurements(ListCreateAPIView):
    """
    Save raw measurements for a tide gauge. Measurements must be given in a
    JSON array.

    - Any measurements which already exist will be updated.
    - The endpoint returns HTTP 201 CREATED regardless of whether the record
      was created or updated.

    Note that an invalid record in the list will cause the entire batch to be
    dropped.
    """

    renderer_classes = replace_json_renderer(
        ListCreateAPIView.renderer_classes)
    permission_classes = (AllowInternalCollectorsReadAndWrite,)

    # I prefer not to override `get_serializer()` just to pass in `many=True`.
    # There may be a better way than using `partial` though.
    # See http://stackoverflow.com/q/28814806/2920176
    serializer_class = functools.partial(RawMeasurementSerializer, many=True)

    def get_serializer_context(self, *args, **kwargs):
        # Augment the default context (containing response etc) with the tide
        # gauge instance referred to by the slug in the request URL.
        # This allows access to the serializer so it can create and query
        # RawMeasurement models.

        c = super(RawMeasurements, self).get_serializer_context(
            *args, **kwargs)
        tide_gauge = TideGauge.objects.get(slug=self.kwargs['tide_gauge_slug'])

        def combine_dicts(a, b):
            return dict(list(a.items()) + list(b.items()))

        return combine_dicts(c, {'tide_gauge': tide_gauge})

    def get_queryset(self):
        return parse_and_get_queryset(
            self.kwargs.get('tide_gauge_slug', None),
            self.request.query_params.get('start', None),
            self.request.query_params.get('end', None))


def parse_and_get_queryset(tide_gauge_or_none, start_or_none, end_or_none):
    tide_gauge = get_tide_gauge(tide_gauge_or_none)
    time_range = parse_time_range(start_or_none, end_or_none)

    validate_time_range(time_range)

    return RawMeasurement.objects.filter(
        tide_gauge=tide_gauge,
        datetime__gte=time_range.start,
        datetime__lt=time_range.end)


def get_tide_gauge(slug_or_none):
    if slug_or_none is None:
        raise MissingParameterError('No tide gauge specified in URL.')

    try:
        return TideGauge.objects.get(slug=slug_or_none)
    except ObjectDoesNotExist:
        raise ObjectNotFoundError(
            'Tide gauge not found: `{}`.'.format(slug_or_none))


def validate_time_range(time_range):
    if time_range.end - time_range.start > datetime.timedelta(hours=24):
        raise TimeRangeError('`start` and `end` must be no greater than '
                             '24 hours apart')
