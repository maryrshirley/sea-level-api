from django.conf.urls import patterns, url

from .views import StatusIndex, SurgePredictions, TidePredictions

urlpatterns = patterns(
    '',

    url(r'^$', StatusIndex.as_view(), name='status-index'),

    url(r'^surge-predictions/$',
        SurgePredictions.as_view(),
        name='surge-predictions'),

    url(r'^tide-predictions/$',
        TidePredictions.as_view(),
        name='tide-predictions'),
)
