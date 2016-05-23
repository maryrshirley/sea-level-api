from django.conf.urls import url

from .views.schedule import Schedule

urlpatterns = (
    url(r'^$', Schedule.as_view(),
        name='schedule'),
)
