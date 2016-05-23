from django.http import Http404

from rest_framework.exceptions import ParseError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin

from api.libs.user_permissions.permissions_classes import (
    AllowInternalCollectorsReadAndWrite)
from ..serializers import (ScheduleSerializer, ScheduleArrivalsListSerializer,
                           ScheduleDeparturesListSerializer)

from ..models import Schedule as ScheduleModel


class Schedule(GenericAPIView, CreateModelMixin):

    permission_classes = (AllowInternalCollectorsReadAndWrite,)
    serializer_class = ScheduleSerializer

    @property
    def many(self):
        return type(self.request.data) is list

    def post(self, request, *args, **kwargs):
        model = self.serializer_class.Meta.model
        existing_object = lambda x: model.objects.existing_object(x)
        data = [request.data] if not self.many else request.data

        processed = []
        update_responses = []

        # Treat later items in the list as newer
        for record in reversed(data):
            if 'code' not in record:
                raise ParseError(detail='Required field code not found')
            code = record['code']
            instance = existing_object(code)

            # Ignore this record if one has been processed already
            if code in processed:
                request.data.remove(record)
                continue

            # Do an update, record already exists
            if instance:
                update_responses.append(self.update_object(instance, record))

                if not self.many:
                    request.data.remove(record)

            processed.append(code)

        # Update only
        if len(request.data) == len(update_responses):
            return Response(update_responses, status=201)

        create_response = self.create(request, *args, **kwargs)

        if not self.many:
            return create_response

        return Response(create_response.data + update_responses, status=201)

    def get_serializer(self, *args, **kwargs):
        kwargs['many'] = kwargs.get('many', self.many)
        return super(Schedule, self).get_serializer(*args, **kwargs)

    def update_object(self, instance, data, partial=False):
        serializer = self.get_serializer(instance, data=data, partial=partial,
                                         many=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return serializer.data

    def perform_update(self, serializer):
        serializer.save()


class ScheduleArrivalsList(ListAPIView):

    permission_classes = (AllowInternalCollectorsReadAndWrite,)
    serializer_class = ScheduleArrivalsListSerializer

    def get_queryset(self, *args, **kwargs):
        location_slug = self.kwargs.get('location_slug', None)
        if not location_slug:
            raise Http404
        return ScheduleModel.objects.filter(destination__slug=location_slug)


class ScheduleDeparturesList(ListAPIView):

    permission_classes = (AllowInternalCollectorsReadAndWrite,)
    serializer_class = ScheduleDeparturesListSerializer

    def get_queryset(self, *args, **kwargs):
        location_slug = self.kwargs.get('location_slug', None)
        if not location_slug:
            raise Http404
        return ScheduleModel.objects.filter(origin__slug=location_slug)
