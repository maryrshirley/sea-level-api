from freezegun import freeze_time

from api.libs.test_utils.schedule import ScheduleMixin

from .base import AdminTest, FunctionalTest, SeleniumTest


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


class ScheduleStatus(SeleniumTest, ScheduleMixin):

    def setUp(self):
        super(ScheduleStatus, self).setUp()
        self.setUpScheduleRequirements()
        self.url = self.live_server_url + self.schedule_status_endpoint

    def tearDown(self):
        self.tearDownScheduleRequirements()
        super(ScheduleStatus, self).tearDown()

    def test_schedule_has_status(self):
        # A schedule exists
        schedule = self.create_schedule_now()

        # User visits the status page
        self.browser.get(self.url)

        # User notices header
        page_header = self.browser \
            .find_element_by_xpath(".//div[@class='page-header']/h1")
        self.assertEquals('Schedules: OK', page_header.text)

        # User notices data table
        table = self.browser \
            .find_element_by_xpath(".//table[@class='table']")

        # User notices the table headings
        th = table.find_elements_by_tag_name('th')
        self.assertEquals(2, len(th))

        self.assertEquals("Location", th[0].text)
        self.assertEquals("Status", th[1].text)

        # User notices the table body
        tbody = table.find_element_by_tag_name('tbody')

        # User notices a table rows
        tr = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(2, len(tr))

        # User notices two table elements
        td = tr[0].find_elements_by_tag_name('td')
        self .assertEqual(2, len(td))

        # User notices the location name matches
        self.assertEquals("Liverpool", td[0].text)

        # User notices two table elements
        td = tr[1].find_elements_by_tag_name('td')
        self .assertEqual(2, len(td))

        # User notices the location name matches
        self.assertEquals("Heysham", td[0].text)

        # User notices the status is OK
        self.assertEquals("OK", td[1].text)

        schedule.delete()

    def test_location_can_be_ignored(self):
        pass
