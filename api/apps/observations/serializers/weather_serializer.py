from rest_framework import serializers

from ..models import WeatherObservation


class WeatherObservationSerializer(serializers.ModelSerializer):

    datetime = serializers.DateTimeField()

    class Meta:
        model = WeatherObservation
        exclude = ('location', 'minute', 'id')

    def update(self, instance, validated_data):
        assert instance.minute.datetime == validated_data['datetime']


class WeatherPrecipitationObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('precipitation',)


class WeatherPressureObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('pressure',)


class WeatherWindGustObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('wind_gust',)


class WeatherWindSpeedObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('wind_speed',)


class WeatherWindDirectionObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('wind_direction',)


class WeatherWindDegreesObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('wind_degrees',)


class WeatherTemperatureObservationSerializer(WeatherObservationSerializer):
    class Meta:
        model = WeatherObservation
        fields = ('temperature',)
