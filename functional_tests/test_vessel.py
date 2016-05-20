from api.libs.test_utils.vessel import VesselMixin

from .base import AdminTest, SeleniumTest


class VesselTest(VesselMixin):
    '''
        As a user: I wish to retrieve a list of vessels.
        AAU: I wish to retrieve information about a vessel.
    '''


class VesselAdminTest(SeleniumTest, AdminTest, VesselMixin):

    def setUp(self):
        super(VesselAdminTest, self).setUp()
        self.setUpAdmin()
        self.loadAdmin()

    def tearDown(self):
        self.tearDownAdmin()
        super(VesselAdminTest, self).tearDown()

    def test_add_vessel(self):
        # As an admin: I wish to create a vessel with imo, name, draft.
        # Add a record
        records = [self.payload_vessel()]

        # The user expects the slug to be autofilled
        del records[0]['slug']

        # The user adds the record
        self.add_record('vessel', 'Vessels', records[0])

        # The user observes the record
        self.check_records(records)
