from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import ugettext as _

from rest_framework import serializers
from rest_framework import mixins, viewsets
from rest_framework.generics import GenericAPIView

from ..models import WeatherObservation

from api.apps.locations.models import Location
from api.libs.user_permissions.permissions_classes import (
    AllowInternalCollectorsReadAndWrite)
from api.libs.param_parsers import InvalidParameterError, parse_time_range
from api.libs.view_helpers import now_rounded


class WeatherEndpoint(viewsets.ModelViewSet):

    def get_object(self, pk=None):
        slug = self.kwargs.get('location_slug')
        queryset = WeatherObservation.objects.filter(location__slug=slug)
        if not queryset:
            raise Http404
        return queryset.order_by('-id')[0]

    def get_serializer_class(self):
        if 'serializer' not in self.kwargs:
            raise ImproperlyConfigured

        return self.kwargs['serializer']


class Weather(mixins.ListModelMixin, GenericAPIView):
    permission_classes = (AllowInternalCollectorsReadAndWrite,)
    lookup_url_kwarg = "location_slug"

    def get_location(self):
        slug = self.kwargs['location_slug']
        try:
            return Location.objects.get(slug=slug)
        except Location.DoesNotExist:
            raise InvalidParameterError

    def get_queryset(self):
        return WeatherObservation.objects.filter(location=self.get_location) \
            .order_by('-id')[:1]

    def get_serializer_class(self):
        if 'serializer' not in self.kwargs:
            raise ImproperlyConfigured

        return self.kwargs['serializer']

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]
            if isinstance(data, list):
                kwargs["many"] = True
        return super(Weather, self).get_serializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WeatherRange(Weather):
    def get_queryset(self):
        location = self.get_location()

        query_params = self.request.query_params
        time_range = parse_time_range(
            query_params.get('start', None),
            query_params.get('end', None)
        )

        if time_range.end > now_rounded():
            raise InvalidParameterError(_("End range cannot be in the future"))

        queryset = WeatherObservation.objects.date_range(location, time_range)

        return queryset


class WeatherRecent(Weather):
    def get_queryset(self):
        location = self.get_location()
        return WeatherObservation.objects.now_minus_24(location)


class WeatherListCreate(WeatherRange, mixins.CreateModelMixin):
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            location = Location.objects.get(slug=self.kwargs['location_slug'])
        except Location.DoesNotExist:
            error = "Could not find location {}" \
                    .format(self.kwargs['location_slug'])
            raise serializers.ValidationError(error)
        serializer.save(location=location)
