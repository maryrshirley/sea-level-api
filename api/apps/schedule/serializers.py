from rest_framework import serializers

from api.apps.locations.models import Location
from ..vessel.models import Vessel
from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):

    departure_datetime = serializers.DateTimeField()
    arrival_datetime = serializers.DateTimeField()
    origin = serializers.SlugRelatedField(
        queryset=Location.objects.all(),
        slug_field='slug'
    )
    destination = serializers.SlugRelatedField(
        queryset=Location.objects.all(),
        slug_field='slug'
    )
    vessel = serializers.SlugRelatedField(
        queryset=Vessel.objects.all(),
        slug_field='imo'
    )

    class Meta:
        model = Schedule
        exclude = ('departure', 'arrival')


class ScheduleDeparturesListSerializer(serializers.ModelSerializer):

    vessel = serializers.SlugRelatedField(read_only=True, slug_field='name')
    departure = serializers.SlugRelatedField(read_only=True,
                                             slug_field='datetime')

    class Meta:
        model = Schedule
        fields = ('vessel', 'departure', 'sea_level')


class ScheduleArrivalsListSerializer(serializers.ModelSerializer):

    vessel = serializers.SlugRelatedField(read_only=True,
                                          slug_field='name')
    arrival = serializers.SlugRelatedField(read_only=True,
                                           slug_field='datetime')

    class Meta:
        model = Schedule
        fields = ('vessel', 'arrival', 'sea_level')
