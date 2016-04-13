import copy

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import ugettext as _

from rest_framework import serializers
from rest_framework import mixins, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

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

    def existing_object(self, slug, record):
        model = self.get_serializer().Meta.model
        return model.objects.existing_object(slug, record['datetime'])

    def post(self, request, *args, **kwargs):
        update_data = []

        data = [request.data] if type(request.data) is dict else request.data
        data = copy.copy(data)

        for record in data:
            instance = self.existing_object(kwargs['location_slug'],
                                            record)
            if instance is not None:
                update_data.append(self.update_object(instance, record))
                request.data.remove(record)

        create_response = self.create(request, *args, **kwargs)
        if not update_data:
            return create_response

        return Response(create_response.data + update_data)

    def update_object(self, instance, data, partial=False):
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return serializer.data

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        try:
            location = Location.objects.get(slug=self.kwargs['location_slug'])
        except Location.DoesNotExist:
            error = "Could not find location {}" \
                    .format(self.kwargs['location_slug'])
            raise serializers.ValidationError(error)
        serializer.save(location=location)