from api.libs.test_utils.location import LocationMixin

from .base import AdminTest, SeleniumTest


class LocationAdminTest(SeleniumTest, AdminTest, LocationMixin):

    def setUp(self):
        super(LocationAdminTest, self).setUp()
        self.setUpAdmin()
        self.loadAdmin()

    def tearDown(self):
        self.tearDownAdmin()
        super(LocationAdminTest, self).tearDown()

    def test_add_location(self):
        # Add a record
        records = [self.payload_location()]
        self.add_record('location', 'Locations', records[0])

        # Check the record now exists
        self.check_records(records)
