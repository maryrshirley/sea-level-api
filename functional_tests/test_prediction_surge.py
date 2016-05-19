import datetime
import pytz

from api.apps.locations.models import Location
from api.apps.predictions.utils import create_surge_prediction
from .base import AdminTest, SeleniumTest

BASE_TIME = datetime.datetime(2014, 8, 1, 10, 0, 0, tzinfo=pytz.UTC)


class SurgeAdminTest(SeleniumTest, AdminTest):

    def setUp(self):
        super(SurgeAdminTest, self).setUp()

        self.setUpAdmin()
        self.loadAdmin()

    def tearDown(self):
        self.tearDownAdmin()
        super(SurgeAdminTest, self).tearDown()

    def test_admin(self):
        location2 = Location.objects.create(slug='location2', name='Location2')

        for minute in range((36 * 60) + 10):
            create_surge_prediction(
                self.location,
                BASE_TIME + datetime.timedelta(minutes=minute),
                0.2)

        # User clicks on the admin page
        admin_page = self.browser. \
            find_element_by_link_text('Surge predictions')
        admin_page.click()

        # User notices the data table
        tbody = self.browser.find_element_by_tag_name('tbody')

        # User notices the table rows
        tr = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(100, len(tr))

        # User notices the row elements
        tr[1].find_element_by_class_name('field-location')
        tr[1].find_element_by_class_name('field-minute')
        tr[1].find_element_by_class_name('field-surge_level')

        # User notices filtering options
        filter_element = self.browser.find_element_by_id('changelist-filter')

        # User notices filter titles
        h3 = filter_element.find_elements_by_tag_name('h3')
        self.assertEqual(1, len(h3))

        self.assertEqual('By location', h3[0].text)
        location2.delete()
