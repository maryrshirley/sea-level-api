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

from .views.weather import WeatherObservations, WeatherRange, WeatherRecent

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
            name='observation-weather-{0}'.format(endpoint)),
    )

'''
    # XXX: These are kept incase we want the latest there
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')$',
        WeatherRange.as_view(),
        {'serializer': WeatherObservationSerializer},
        name='observation-weather'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/recent$',
        WeatherRecent.as_view(),
        {'serializer': WeatherObservationSerializer},
        name='observation-weather-recent'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/precipitation$',
        WeatherRange.as_view(),
        {'serializer': WeatherPrecipitationObservationSerializer},
        name='observation-weather-precipitation'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/precipitation/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherPrecipitationObservationSerializer},
        name='observation-weather-precipitation'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/pressure$',
        WeatherRange.as_view(),
        {'serializer': WeatherPressureObservationSerializer},
        name='observation-weather-pressure'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/pressure/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherPressureObservationSerializer},
        name='observation-weather-pressure'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-gust$',
        WeatherRange.as_view(),
        {'serializer': WeatherWindGustObservationSerializer},
        name='observation-weather-wind-gust'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-gust/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherWindGustObservationSerializer},
        name='observation-weather-wind-gust'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-speed$',
        WeatherRange.as_view(),
        {'serializer': WeatherWindSpeedObservationSerializer},
        name='observation-weather-wind-speed'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-speed/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherWindSpeedObservationSerializer},
        name='observation-weather-wind-speed'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-direction$',
        WeatherRange.as_view(),
        {'serializer': WeatherWindDirectionObservationSerializer},
        name='observation-weather-wind-direction'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-direction/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherWindDirectionObservationSerializer},
        name='observation-weather-wind-direction'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-degrees$',
        WeatherRange.as_view(),
        {'serializer': WeatherWindDegreesObservationSerializer},
        name='observation-weather-wind-degrees'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/wind-degrees/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherWindDegreesObservationSerializer},
        name='observation-weather-wind-degrees'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/temperature$',
        WeatherRange.as_view(),
        {'serializer': WeatherTemperatureObservationSerializer},
        name='observation-weather-temperature'),
    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/temperature/recent$',
        WeatherEndpoint.as_view({'get': 'retrieve'}),
        {'serializer': WeatherTemperatureObservationSerializer},
        name='observation-weather-temperature'),

'''
