from django.conf import settings
from django.conf.urls import url

from .views.schedule import (Schedule, ScheduleArrivalsList,
                             ScheduleDeparturesList)

urlpatterns = (
    url(r'^$', Schedule.as_view(),
        name='schedule'),
    url(r'^(?P<location_slug>' + settings.SLUG_REGEX + ')/departures/$',
        ScheduleDeparturesList.as_view(),
        name='schedule-departures'),
    url(r'^(?P<location_slug>' + settings.SLUG_REGEX + ')/arrivals/$',
        ScheduleArrivalsList.as_view(),
        name='schedule-arrivals'),
)
