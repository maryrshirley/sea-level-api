from django.test import TestCase

from api.libs.test_utils.notification import NotificationMixin


class TestNotification(TestCase, NotificationMixin):

    def setUp(self):
        super(TestNotification, self).setUp()
        self.setUpNotificationRequirements()

    def tearDown(self):
        self.tearDownNotificationRequirements()
        super(TestNotification, self).tearDown()

    def test_defaults(self):
        notification = self.create_notification()

        notification.delete()
