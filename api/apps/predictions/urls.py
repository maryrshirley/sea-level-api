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
    WeatherTemperatureSerializer,
    WeatherTypeSerializer)
from .views import (TideLevels, TideLevelsNow, TideWindows, TideWindowsNow,
                    SurgeLevels)
from .views.weather import (WeatherPredictions, WeatherRange, WeatherNow,
                            WeatherLatest)

SLUG_RE = settings.SLUG_REGEX

EndPoint = namedtuple('EndPoint', 'endpoint, serializer')

endpoints = (
    EndPoint('precipitation', WeatherPrecipitationSerializer),
    EndPoint('pressure', WeatherPressureSerializer),
    EndPoint('wind-gust', WeatherWindGustSerializer),
    EndPoint('wind-speed', WeatherWindSpeedSerializer),
    EndPoint('wind-direction', WeatherWindDirectionSerializer),
    EndPoint('wind-degrees', WeatherWindDegreesSerializer),
    EndPoint('temperature', WeatherTemperatureSerializer),
    EndPoint('weather-type', WeatherTypeSerializer)
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
        name='prediction-weather'),

    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')$',
        WeatherPredictions.as_view(),
        {'serializer': WeatherSerializer},
        name='prediction-weather'),

    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/now$',
        WeatherNow.as_view(),
        {'serializer': WeatherSerializer},
        name='prediction-weather-now'),

    url(r'^weather/(?P<location_slug>' + SLUG_RE + ')/latest$',
        WeatherLatest.as_view(),
        {'serializer': WeatherSerializer},
        name='weather-latest'),
]


for endpoint in endpoints:
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherRange.as_view(),
            {'serializer': endpoint.serializer},
            name='prediction-weather-{0}'.format(endpoint)),
    )
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}/now$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherNow.as_view(),
            {'serializer': endpoint.serializer},
            name='weather-now-{0}'.format(endpoint)),
    )
    urlpatterns.append(
        url(r'^weather/(?P<location_slug>{0})/{1}/latest$'
            .format(SLUG_RE, endpoint.endpoint),
            WeatherLatest.as_view(),
            {'serializer': endpoint.serializer},
            name='prediction-weather-{0}'.format(endpoint)),
    )
