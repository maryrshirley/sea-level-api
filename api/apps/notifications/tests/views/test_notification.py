import json

from django.apps import apps

from nose.tools import assert_equal
from nose_parameterized import parameterized

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.apps.users.helpers import create_user
from api.libs.test_utils.notification import NotificationMixin


_URL = NotificationMixin.notifications_endpoint

_URL_LIVERPOOL = _URL.format('liverpool')
_URL_HEYSHAM = _URL.format('heysham')

url_testcases = [
    (_URL_LIVERPOOL, 'GET, HEAD, OPTIONS'),
]

User = apps.get_model('auth', 'User')


class TestNotification(APITestCase, NotificationMixin):

    def setUp(self):
        super(TestNotification, self).setUp()
        self.permitted = create_user('permitted', is_internal_collector=True)
        self.forbidden = create_user('forbidden', is_internal_collector=False)
        self.token_permitted, _ = Token.objects.get_or_create(
            user=self.permitted)
        self.token_forbidden, _ = Token.objects.get_or_create(
            user=self.forbidden)
        self.token = self.token_permitted
        self.setUpNotificationRequirements()

    def tearDown(self):
        self.permitted.delete()
        self.forbidden.delete()
        self.token_permitted.delete()
        self.token_forbidden.delete()
        self.tearDownNotificationRequirements()
        super(TestNotification, self).tearDown()

    @property
    def auth(self):
        return {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}

    @parameterized.expand(url_testcases)
    def test_that_http_exist_options_allowed(self, url, allow):
        response = self.client.options(url, **self.auth)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])

    def test_that_no_authentication_returns_401_status(self):
        response = self.client.options(_URL_LIVERPOOL)
        assert_equal(401, response.status_code)

    def test_that_user_without_add__permission_returns_403_status(self):
        self.token = self.token_forbidden
        response = self.client.options(_URL_LIVERPOOL, **self.auth)
        assert_equal(403, response.status_code)

    def assertGetNotifications(self, status_code, items, url=_URL_LIVERPOOL):
        response = self.client.get(url, **self.auth)
        assert_equal(status_code, response.status_code)
        data = json.loads(response.content.decode('utf-8'))
        assert_equal(len(items), len(data))

    def test_that_http_get_returns_record(self):
        notification = self.create_notification()
        self.assertGetNotifications(200, [notification])
        notification.delete()

    def test_that_http_get_relevant_notifications(self):
        notifications = [self.create_notification(),
                         self.create_notification(location__slug='heysham')]

        self.assertGetNotifications(200, [notifications[0]])
        self.assertGetNotifications(200, [notifications[1]], url=_URL_HEYSHAM)

        for notification in notifications:
            notification.delete()
