from collections import namedtuple

from django.conf.urls import url
from django.conf import settings

from .serializers.weather_serializer import (
    WeatherSerializer,
    WeatherPrecipitationSerializer,
    WeatherPressureSerializer,
    WeatherWindGustSerializer,
    WeatherWindSpeedSerializer,
    WeatherWindDirectionSerializer,
    WeatherWindDegreesSerializer,
    WeatherTemperatureSerializer)
from .views import (TideLevels, TideLevelsNow, TideWindows, TideWindowsNow,
                    SurgeLevels)
from .views.weather import WeatherPredictions, WeatherRange, WeatherNow

SLUG_RE = settings.SLUG_REGEX

EndPoint = namedtuple('EndPoint', 'endpoint, serializer')

endpoints = (
    EndPoint('precipitation', WeatherPrecipitationSerializer),
    EndPoint('pressure', WeatherPressureSerializer),
    EndPoint('wind-gust', WeatherWindGustSerializer),
    EndPoint('wind-speed', WeatherWindSpeedSerializer),
    EndPoint('wind-direction', WeatherWindDirectionSerializer),
    EndPoint('wind-degrees', WeatherWindDegreesSerializer),
    EndPoint('temperature', WeatherTemperatureSerializer)
)

urlpatterns = [
    url(r'^tide-levels/$', TideLevels.as_view(), name='tide-levels'),
    url(r'^tide-windows/$', TideWindows.as_view(), name='tide-windows'),

    url(r'^tide-levels/(?P<location_slug>' + SLUG_RE + ')/$',
        TideLevels.as_view(),
        name='tide-levels'),

    url(r'^surge-levels/(?P<location_slug>' + SLUG_RE + ')/$',
        SurgeLevels.as_view(),
        name='surge-levels'),

    url(r'^tide-levels/(?P<location_slug>' + SLUG_RE + ')/now/$',
        TideLevelsNow.as_view(),
        name='tide-levels'),

    url(r'^tide-windows/(?P<location_slug>' + SLUG_RE + ')/$',
        TideWindows.as_view(),
        name='tide-windows'),

    url(r'^tide-windows/(?P<location_slug>' + SLUG_RE + ')/now/$',
        TideWindowsNow.as_view(),
        name='tide-windows'),

    url(r'^weather/$',
        WeatherPredictions.as_view(),
        {'serializer': WeatherSerializer},
        name='weather'),

    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')$',
        WeatherPredictions.as_view(),
        {'serializer': WeatherSerializer},
        name='weather'),

    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/now$',
        WeatherNow.as_view(),
        {'serializer': WeatherSerializer},
        name='weather-now'),
]


for endpoint in endpoints:
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherRange.as_view(),
            {'serializer': endpoint.serializer},
            name='weather-{0}'.format(endpoint)),
    )
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}/now$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherNow.as_view(),
            {'serializer': endpoint.serializer},
            name='weather-{0}'.format(endpoint)),
    )

'''
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/precipitation$',
        WeatherPrecipitation.as_view({'get': 'retrieve'}),
        name='weather-precipitation'),
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/pressure$',
        WeatherPressure.as_view({'get': 'retrieve'}),
        name='weather-pressure'),
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/wind-gust$',
        WeatherWindGust.as_view({'get': 'retrieve'}),
        name='weather-wind-gust'),
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/wind-speed$',
        WeatherWindSpeed.as_view({'get': 'retrieve'}),
        name='weather-wind-speed'),
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/wind-direction$',
        WeatherWindDirection.as_view({'get': 'retrieve'}),
        name='weather-wind-direction'),
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/wind-degrees$',
        WeatherWindDegrees.as_view({'get': 'retrieve'}),
        name='weather-wind-degrees'),
    url(r'^weather/(?P<location_slug>' + SLUG_REGEX + ')/temperature$',
        WeatherTemperature.as_view({'get': 'retrieve'}),
        name='weather-temperature'),
'''
