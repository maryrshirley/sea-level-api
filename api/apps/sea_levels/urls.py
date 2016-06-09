from django.conf.urls import patterns, url
from django.conf import settings

from .views import (SeaLevels, SeaLevelsLatest, SeaLevelsNow,
                    SeaLevelsWindows, SeaLevelWindowsNow)

location_pattern = '(?P<location_slug>{0})'.format(settings.SLUG_REGEX)

urlpatterns = patterns(
    '',

    url(r'^$', SeaLevels.as_view(), name='sea-levels'),

    url(r'^{0}/$'.format(location_pattern),
        SeaLevels.as_view(),
        name='sea-levels'),

    url(r'^{0}/now/$'.format(location_pattern),
        SeaLevelsNow.as_view(),
        name='sea-levels'),

    url(r'^{0}/latest/$'.format(location_pattern),
        SeaLevelsLatest.as_view(),
        name='sea-levels-latest'),

    url(r'^{0}/windows$'.format(location_pattern),
        SeaLevelsWindows.as_view(),
        name='sea-levels-windows-range'),

    url(r'^{0}/windows/now/$'.format(location_pattern),
        SeaLevelWindowsNow.as_view(),
        name='sea-levels-windows-now'),
)
