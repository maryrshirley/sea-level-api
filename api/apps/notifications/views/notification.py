from django.http import Http404

from rest_framework.generics import ListAPIView

from api.libs.user_permissions.permissions_classes import (
    AllowInternalCollectorsReadAndWrite)

from ..models import Notification
from ..serializers import NotificationSerializer


class Notifications(ListAPIView):

    permission_classes = (AllowInternalCollectorsReadAndWrite,)
    serializer_class = NotificationSerializer

    def get_queryset(self, *args, **kwargs):
        location_slug = self.kwargs.get('location_slug', None)
        if not location_slug:
            raise Http404
        return Notification.objects.filter(location__slug=location_slug)
