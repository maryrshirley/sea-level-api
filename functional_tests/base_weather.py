from api.apps.locations.models import Location
from api.libs.test_utils.weather import (CreateObservationMixin,
                                         CreatePredictionMixin)

from .base import AdminTest, SeleniumTest


class WeatherAdminTest(SeleniumTest, AdminTest, CreateObservationMixin,
                       CreatePredictionMixin):

    def setUp(self):
        super(WeatherAdminTest, self).setUp()

        self.setUpAdmin()
        self.loadAdmin()

    def tearDown(self):
        self.tearDownAdmin()
        super(WeatherAdminTest, self).tearDown()

    def _test_admin(self, objects, label, assert_function):
        location2 = Location.objects.create(slug='location2', name='Location2')

        # User clicks on the admin page
        admin_page = self.browser. \
            find_element_by_link_text('Weather {0}'.format(label))
        admin_page.click()

        # User notices the number of elements
        paginator = self.browser.find_element_by_class_name('paginator')
        self.assertEquals('2 weather {0}'.format(label), paginator.text)

        # User notices the data table
        tbody = self.browser.find_element_by_tag_name('tbody')

        # User notices the table rows
        tr = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(2, len(tr))

        # User notices the row elements
        location_field = tr[1].find_element_by_class_name('field-location')
        supplier_field = tr[1].find_element_by_class_name('field-supplier')
        '''
        datetime_field = tr[1].find_element_by_class_name('field-datetime')
        datetime = formats.date_format(objects[0].datetime,
                                       "DATETIME_FORMAT")
        '''

        self.assertEqual(objects[0].location.__str__(), location_field.text)
        self.assertEqual(objects[0].get_supplier_display(),
                         supplier_field.text)
        '''
        self.assertEqual(datetime, datetime_field.text)
        '''
        assert_function(tr[1], objects[0])

        # User notices filtering options
        filter_element = self.browser.find_element_by_id('changelist-filter')

        # User notices filter titles
        h3 = filter_element.find_elements_by_tag_name('h3')
        self.assertEqual(2, len(h3))

        self.assertEqual('By location', h3[0].text)
        self.assertEqual('By supplier', h3[1].text)

        location2.delete()
