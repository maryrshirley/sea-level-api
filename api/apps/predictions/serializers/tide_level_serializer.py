from rest_framework import serializers

from ..models import Prediction


class TideLevelSerializer(serializers.ModelSerializer):
    datetime = serializers.SerializerMethodField('get_datetime')

    class Meta:
        model = Prediction
        resource_name = 'tide_levels'
        fields = ('tide_level', 'datetime')

    def get_datetime(self, obj):
        return obj.minute.datetime
