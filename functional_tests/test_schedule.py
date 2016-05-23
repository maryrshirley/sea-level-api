from freezegun import freeze_time

from api.libs.test_utils.schedule import ScheduleMixin

from .base import AdminTest, FunctionalTest, SeleniumTest

'''
        A schedule for a vessel moving between two locations:
            As a collector: I wish to upload schedule information with etd,
                eta, departure, destination.
'''


class ScheduleTest(FunctionalTest, ScheduleMixin):

    def setUp(self):
        super(ScheduleTest, self).setUp()
        self.setUpScheduleRequirements()

    def tearDown(self):
        self.tearDownScheduleRequirements()
        super(ScheduleTest, self).tearDown()

    def test_schedule_arrival_retrieve(self):
        # As a user, I wish to retrieve arrivals for a location
        #   with: arrival_timestamp, vessel_name, predicted_water_level
        payload = self.payload_schedule()
        schedule = self.create_schedule(payload=payload)

        url = self.live_server_url + \
            self.schedule_departures_endpoint.format('liverpool')

        with freeze_time(payload['departure'].datetime):
            data = self.assertRecordJSONExists(url)

        self.assertPayloadMatchesData(data[0],
                                      self.payload_schedule_read(payload))

        schedule.delete()

    def test_schedule_departure_retrieve(self):
        # As a user, I wish to retirieve departures for a location
        #   with: arrival_timestamp, vessel_name, predicted_water_level
        payload = self.payload_schedule()
        schedule = self.create_schedule(payload=payload)

        url = self.live_server_url + \
            self.schedule_arrivals_endpoint.format('heysham')

        with freeze_time(payload['departure'].datetime):
            data = self.assertRecordJSONExists(url)

        self.assertPayloadMatchesData(data[0],
                                      self.payload_schedule_read(payload))

        schedule.delete()


class ScheduleCollectorTest(FunctionalTest, ScheduleMixin):

    def setUp(self):
        super(ScheduleCollectorTest, self).setUp()
        self.setUpScheduleRequirements()

    def tearDown(self):
        self.tearDownScheduleRequirements()
        super(ScheduleCollectorTest, self).tearDown()

    def test_create_schedule(self):
        # A user has schedule data
        payload = self.values_payload(self.payload_schedule())

        # The user has a url
        url = self.live_server_url + self.schedule_endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(url, [payload])

        # XXX: Query a range endpoint

        # XXX: Query a latest endpoint


class ScheduleAdminTest(SeleniumTest, AdminTest, ScheduleMixin):

    def setUp(self):
        super(ScheduleAdminTest, self).setUp()

        self.setUpScheduleRequirements()

        self.setUpAdmin()
        self.loadAdmin()

    def tearDown(self):
        self.tearDownAdmin()

        self.tearDownScheduleRequirements()

        super(ScheduleAdminTest, self).tearDown()

    def test_retrieve_schedule(self):
        # As an admin: I wish to retrieve a schedule with origin, destination,
        #    vessel, departure, arrival, code

        # A schedule exists
        schedule_payload = self.payload_schedule()
        schedule = self.create_schedule(schedule_payload)

        # The user loads the schedule page
        self.load_model_page('schedule', 'Schedules')

        # The user observes the record
        self.check_records([schedule_payload])

        schedule.delete()

        # XXX: Check __str__ value
