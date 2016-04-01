from rest_framework import serializers

from ..models import WeatherPrediction


class WeatherSerializer(serializers.ModelSerializer):

    valid_from = serializers.DateTimeField()
    valid_to = serializers.DateTimeField()

    class Meta:
        exclude = ('location', 'id', 'minute_to', 'minute_from')
        model = WeatherPrediction

    def update(self, instance, validated_data):
        assert instance.minute.valid_from == validated_data['valid_from']
        assert instance.minute.valid_to == validated_data['valid_to']


class WeatherPrecipitationSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('precipitation',)


class WeatherPressureSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('pressure',)


class WeatherWindGustSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('wind_gust',)


class WeatherWindSpeedSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('wind_speed',)


class WeatherWindDirectionSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('wind_direction',)


class WeatherWindDegreesSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('wind_degrees',)


class WeatherTemperatureSerializer(WeatherSerializer):
    class Meta:
        model = WeatherPrediction
        fields = ('temperature',)
