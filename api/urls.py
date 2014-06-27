from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from rest_framework.reverse import reverse

from .api_root_view import ApiRoot

urlpatterns = [
    # Examples:
    # url(r'^$', 'api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', RedirectView.as_view(url='/1/', permanent=False)),

    url(r'^1/$', ApiRoot.as_view(), name='api-root'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^1/locations/', include('api.apps.locations.urls')),
    url(r'^1/predictions/', include('api.apps.predictions.urls')),
]
