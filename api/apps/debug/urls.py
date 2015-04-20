from django.conf.urls import patterns, url

from .views import HTTP500, MailAdmins

urlpatterns = patterns(
    '',

    url(r'^500/$', HTTP500.as_view(), name='debug-http-500'),
    url(r'^mail-admins/$', MailAdmins.as_view(), name='debug-mail-admins'),
)
