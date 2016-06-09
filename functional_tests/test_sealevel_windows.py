from .base import FunctionalTest

from freezegun import freeze_time

from api.libs.test_utils.sea_level import SeaLevelMixin


class SeaLevelWindowTest(FunctionalTest, SeaLevelMixin):

    def setUp(self):
        super(SeaLevelWindowTest, self).setUp()
        self.setUpSeaLevelRequirements()

    def tearDown(self):
        self.tearDownSeaLevelRequirements()
        super(SeaLevelWindowTest, self).tearDown()

    def test_retrieve_now(self):
        with freeze_time(self.tide_predictions[0].minute.datetime):
            # A user passes a url for the now
            url = self.endpoint_url(self.get_url('windows_now_endpoint'))

            # A user requests the range record
            data = self.assertRecordJSONExists(url)

            self.assertEqual(1, len(data))

            expected = self.sea_level_window_json()
            self.assertDictEqual(expected, data[0])

    def test_retrieve_range(self):

        # A user passes a url for a range between a start and end
        url = self.endpoint_url(self.get_url('windows_range_endpoint'))

        # A user requests the range record
        data = self.assertRecordJSONExists(url)

        self.assertEqual(1, len(data))
