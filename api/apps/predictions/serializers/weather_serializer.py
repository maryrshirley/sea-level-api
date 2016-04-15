from rest_framework import serializers

from ..models import WeatherPrediction


class WeatherSerializer(serializers.ModelSerializer):

    valid_from = serializers.DateTimeField()
    valid_to = serializers.DateTimeField()

    class Meta:
        exclude = ('location', 'id', 'minute_to', 'minute_from')
        model = WeatherPrediction

    def update(self, instance, validated_data):
        super(WeatherSerializer, self).update(instance, validated_data)
        assert instance.minute_from.datetime == validated_data['valid_from']
        assert instance.minute_to.datetime == validated_data['valid_to']
        return instance


class WeatherPrecipitationSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'precipitation',)


class WeatherPressureSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'pressure',)


class WeatherWindGustSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'wind_gust',)


class WeatherWindSpeedSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'wind_speed',)


class WeatherWindDirectionSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'wind_direction',)


class WeatherWindDegreesSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'wind_degrees',)


class WeatherTemperatureSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('valid_from', 'valid_to', 'temperature',)
