from django.conf.urls import patterns, url
from django.conf import settings

from .views import RawMeasurements, RawMeasurementsIndex

urlpatterns = patterns(
    '',

    url(r'^raw-measurements/$',
        RawMeasurementsIndex.as_view(),
        name='tide-gauge-raw-masurements-index'),

    url(r'^raw-measurements/(?P<tide_gauge_slug>' +
        settings.SLUG_REGEX + ')/$',
        RawMeasurements.as_view(),
        name='tide-gauge-raw-measurements'),
)
