from api.libs.test_utils.notification import NotificationMixin

from .base import AdminTest, FunctionalTest, SeleniumTest


class NotificationGeneratorTest(object):
    '''
    As a cron, I wish to run a command in a schedule.
    AAC: I wish to create a notification with location, schedule, vessel,
            category, status
    '''


class NotificationAdminTest(AdminTest, SeleniumTest, NotificationMixin):

    def setUp(self):
        super(NotificationAdminTest, self).setUp()
        self.setUpNotificationRequirements()
        self.setUpAdmin()
        self.loadAdmin()

    def tearDown(self):
        self.tearDownAdmin()
        self.tearDownNotificationRequirements()
        super(NotificationAdminTest, self).tearDown()

    def test_add_notification(self):
        # As an admin: I wish to create a notification
        # Add a record
        records = [self.admin_notification_payload(
            self.payload_notification())]

        # The user adds the record
        self.add_record('notification', 'Notifications', records[0])

        # The user observes the record
        self.check_records(records)


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
