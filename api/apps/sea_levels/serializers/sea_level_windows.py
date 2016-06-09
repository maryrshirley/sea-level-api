from django.conf import settings
from rest_framework import serializers

from ..models import CombinedPredictionObservation


class SeaLevelWindowsSerializer(serializers.Serializer):
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    high_tide = serializers.SerializerMethodField()

    class Meta:
        model = CombinedPredictionObservation

    @staticmethod
    def _serialize_prediction(prediction):
        return {
            'datetime': prediction.datetime.strftime(
                settings.DATETIME_FORMAT),
            'sea_level': prediction.predicted_sea_level
        }

    def get_start(self, obj):
        return self._serialize_prediction(obj.start_prediction)

    def get_end(self, obj):
        return self._serialize_prediction(obj.end_prediction)

    @staticmethod
    def get_duration(obj):
        """
        Predictions are minutely, and the time window is defined by the first
        and last minute where the level is above a certain amount. That means
        the duration is *inclusive* of the final time - so we add a minute.
        """
        timediff = (obj.end_prediction.datetime -
                    obj.start_prediction.datetime)
        return {'total_seconds': timediff.total_seconds() + 60}

    def get_high_tide(self, obj):
        return self._serialize_prediction(obj.high_tide_prediction)
