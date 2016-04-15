from collections import namedtuple

from django.conf.urls import url
from django.conf import settings

from .serializers.weather_serializer import (
    WeatherObservationSerializer,
    WeatherPrecipitationObservationSerializer,
    WeatherPressureObservationSerializer,
    WeatherWindGustObservationSerializer,
    WeatherWindSpeedObservationSerializer,
    WeatherWindDirectionObservationSerializer,
    WeatherWindDegreesObservationSerializer,
    WeatherTemperatureObservationSerializer)

from .views.weather import (WeatherObservations, WeatherRange, WeatherRecent,
                            WeatherLatest)

SLUG_RE = settings.SLUG_REGEX

EndPoint = namedtuple('EndPoint', 'endpoint, serializer')

endpoints = (
    EndPoint('precipitation', WeatherPrecipitationObservationSerializer),
    EndPoint('pressure', WeatherPressureObservationSerializer),
    EndPoint('wind-gust', WeatherWindGustObservationSerializer),
    EndPoint('wind-speed', WeatherWindSpeedObservationSerializer),
    EndPoint('wind-direction', WeatherWindDirectionObservationSerializer),
    EndPoint('wind-degrees', WeatherWindDegreesObservationSerializer),
    EndPoint('temperature', WeatherTemperatureObservationSerializer)
)

urlpatterns = [
    url(r'^weather/$',
        WeatherObservations.as_view(),
        {'serializer': WeatherObservationSerializer},
        name='observation-weather'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')$',
        WeatherObservations.as_view(),
        {'serializer': WeatherObservationSerializer},
        name='observation-weather'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/recent$',
        WeatherRecent.as_view(),
        {'serializer': WeatherObservationSerializer},
        name='weather-recent'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/latest$',
        WeatherLatest.as_view(),
        {'serializer': WeatherObservationSerializer},
        name='observation-weather-recent'),
]

for endpoint in endpoints:
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherRange.as_view(),
            {'serializer': endpoint.serializer},
            name='observation-weather-{0}'.format(endpoint)),
    )
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}/recent$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherRecent.as_view(),
            {'serializer': endpoint.serializer},
            name='weather-recent-{0}'.format(endpoint)),
    )
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}/latest$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherLatest.as_view(),
            {'serializer': endpoint.serializer},
            name='observation-weather-{0}'.format(endpoint)),
    )
