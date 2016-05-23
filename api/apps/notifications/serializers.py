from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    vessel = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Notification
        fields = ('timestamp', 'category', 'status', 'vessel')
