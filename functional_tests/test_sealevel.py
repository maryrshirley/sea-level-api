import datetime

from api.libs.test_utils.datetime_utils import delta
from api.apps.predictions.utils import create_tide_prediction
from api.libs.test_utils.mixins import LocationMixin

from .base import FunctionalTest


class SeaLevelTest(FunctionalTest, LocationMixin):

    endpoint = '/1/sea-levels/liverpool'

    def setUp(self):
        super(SeaLevelTest, self).setUp()
        self.setUpLocation()
        self.create_over_twenty_four_hours_of_tide(self.location)

    def tearDown(self):
        self.tearDownLocation()
        super(SeaLevelTest, self).tearDown()

    def create_over_twenty_four_hours_of_tide(cls, location):
        cls.base_time = delta(hours=1)

        day = 86400

        minutes = [-10, -9, -8,
                   0, 1, 2, 3, 4,
                   day + 1, day + 2, day + 3]

        for minute in minutes:
            create_tide_prediction(
                location,
                cls.base_time + datetime.timedelta(minutes=minute),
                5
            )

    def test_measurement_latest(self):
        latest_url = "{0}{1}/latest/".format(self.live_server_url,
                                             self.endpoint)

        data = self.assertRecordJSONExists(latest_url)
        self.assertEqual(1, len(data['sea_levels']))
