from rest_framework import serializers
from ..models import RawMeasurement

import logging
logger = logging.getLogger(__name__)


class RawMeasurementListSerializer(serializers.ListSerializer):
    class Meta:
        resource_name = 'raw_measurements'


class RawMeasurementSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    height = serializers.FloatField()

    class Meta:
        list_serializer_class = RawMeasurementListSerializer

    def create(self, validated_data):
        """
        Create *or update* a RawMeasurement based on the tide gauge and
        datetime.
        """
        logging.debug('RawMeasurementSerializer.create({})'.format(
            validated_data))

        height = validated_data.pop('height')

        (instance, was_created) = RawMeasurement.objects.update_or_create(
            tide_gauge=self.context['tide_gauge'],
            datetime=validated_data['datetime'],
            defaults={'height': height})
        return instance
