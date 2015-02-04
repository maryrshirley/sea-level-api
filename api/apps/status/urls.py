from django.conf.urls import patterns, url

from .views import StatusAll, SurgePredictions, TidePredictions

urlpatterns = patterns(
    '',

    url(r'^all/$', StatusAll.as_view(), name='status-all'),

    url(r'^surge-predictions/$',
        SurgePredictions.as_view(),
        name='surge-predictions'),

    url(r'^tide-predictions/$',
        TidePredictions.as_view(),
        name='tide-predictions'),
)
