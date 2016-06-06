from django.conf import settings
from django.conf.urls import url

from rest_framework.authtoken.views import obtain_auth_token

from .views.token import auth_code, email_token, validate_token

urlpatterns = [
    url(r'^$', obtain_auth_token),
    url(r'^validate$', validate_token),
    url(r'^email$', email_token, {'callback': '/login/code'}),
    url(r'^code/(?P<login_code>' + settings.SLUG_REGEX + ')/$',
        auth_code, name='auth-code'),
    url(r'^code/$',
        auth_code, name='auth-code'),
]
