from api.libs.test_utils.notification import NotificationMixin

from .base import FunctionalTest


class NotificationGeneratorTest(object):
    '''
    As a cron, I wish to run a command in a schedule.
    AAC: I wish to create a notification with location, schedule, vessel,
            category, status
    '''


class NotificationAdminTest(object):
    # XXX: Ignore admin notifications for now
    pass


class NotificationTest(FunctionalTest, NotificationMixin):

    endpoint = '/1/notifications/liverpool/'

    def setUp(self):
        super(NotificationTest, self).setUp()
        self.setUpNotificationRequirements()

    def tearDown(self):
        self.tearDownNotificationRequirements()
        super(NotificationTest, self).tearDown()

    def test_notification_retrieve(self):
        # As a user: I wish to retrieve notifications for a location
        # AAU: I wish to retrieve a notification with timestamp in port,
        #   category, status

        # A notification exists in the database
        payload = self.payload_notification()
        notification = self.create_notification(payload=payload)

        # A user has a url
        url = self.live_server_url + self.endpoint

        # The user retrieves the notifications
        data = self.assertRecordJSONExists(url)

        # The notification matches our expected values
        self.assertPayloadMatchesData(data[0],
                                      self.payload_notifications_read(payload))

        notification.delete()
