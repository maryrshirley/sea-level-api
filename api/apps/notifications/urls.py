from django.conf.urls import url
from django.conf import settings

from .views.notification import Notifications

urlpatterns = (
    url(r'^(?P<location_slug>' + settings.SLUG_REGEX + ')/$',
        Notifications.as_view(),
        name='notifications'),
)
