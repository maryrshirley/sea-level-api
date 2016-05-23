from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    location = serializers.SlugRelatedField(slug_field='slug', read_only=True)

    class Meta:
        model = Notification
        fields = ('location', 'timestamp', 'category', 'status', )
