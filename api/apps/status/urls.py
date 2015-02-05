from django.conf import settings
from django.conf.urls import patterns, url

from .views import (StatusIndex, StatusAll, SurgePredictions, TidePredictions,
                    Observations)

urlpatterns = patterns(
    '',

    url(r'^$', StatusIndex.as_view(), name='status-index'),

    url(r'^all/$', StatusAll.as_view(), name='status-all'),

    url(r'^surge-predictions/$',
        SurgePredictions.as_view(),
        name='surge-predictions'),

    url(r'^tide-predictions/$',
        TidePredictions.as_view(),
        name='tide-predictions'),

    url(r'^observations/(?P<location_slug>' + settings.SLUG_REGEX + ')/$',
        Observations.as_view(),
        name='observations'),
)
