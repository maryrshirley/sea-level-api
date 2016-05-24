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
        slug_field='slug'
    )

    class Meta:
        model = Schedule
        exclude = ('departure', 'arrival')

    def sea_level(self, location, minute):

        surges = location.surge_predictions.filter(minute=minute) \
            .order_by('minute__datetime')
        tides = location.tide_predictions.filter(minute=minute) \
            .order_by('minute__datetime')

        if not len(surges) or not len(tides):
            return None

        return tides[0].tide_level + surges[0].surge_level

    def save(self, **kwargs):
        instance = super(ScheduleSerializer, self).save(**kwargs)

        instance.depature_sea_level = self.sea_level(instance.origin,
                                                     instance.departure)
        instance.arrival_sea_level = self.sea_level(instance.destination,
                                                    instance.arrival)

        instance.save()

        return instance


class ScheduleDeparturesListSerializer(serializers.ModelSerializer):

    vessel = serializers.SlugRelatedField(read_only=True, slug_field='name')
    departure = serializers.SlugRelatedField(read_only=True,
                                             slug_field='datetime')

    class Meta:
        model = Schedule
        fields = ('vessel', 'departure', 'departure_sea_level')


class ScheduleArrivalsListSerializer(serializers.ModelSerializer):

    vessel = serializers.SlugRelatedField(read_only=True,
                                          slug_field='name')
    arrival = serializers.SlugRelatedField(read_only=True,
                                           slug_field='datetime')

    class Meta:
        model = Schedule
        fields = ('vessel', 'arrival', 'arrival_sea_level')
