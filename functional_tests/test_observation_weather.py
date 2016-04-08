from .base import FunctionalTest

from api.libs.test_utils.datetime_utils import delta
from api.libs.view_helpers import format_datetime


class ObservationWeatherTest(FunctionalTest):

    endpoint = '/1/observations/weather/liverpool'

    def test_can_save_observation(self):
        # A user has observation data
        payload = [{
            'precipitation': 1,
            'pressure': 2,
            'wind_gust': 3,
            'wind_speed': 4,
            'wind_direction': 'SSW',
            'wind_degrees': 1,
            'temperature': 6,
            'datetime': format_datetime(delta()),
        }]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(self.live_server_url + self.endpoint, payload)

        # The user queries for the recent record
        base_url = self.live_server_url + self.endpoint
        recent_url = "{0}/recent".format(base_url)
        data = self.assertRecordJSONExists(recent_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

        # The user queries for a range record
        range_url = '{0}?start={1}&end={2}' \
            .format(base_url, format_datetime(delta(hours=-1)),
                    format_datetime(delta()))
        data = self.assertRecordJSONExists(range_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

        # The user can has individual endpoints to query
        endpoints = [key for key in payload[0].keys() if not key == 'datetime']

        # The user queries each endpoint
        for endpoint in endpoints:
            url = "{0}/{1}/recent".format(base_url, endpoint.replace('_', '-'))

            # The user receives a JSON response from the endpoint
            data = self.assertRecordJSONExists(url)

            # The JSON response contains the observation data
            self.assertIn(endpoint, data[0])
            self.assertEqual(payload[0][endpoint], data[0][endpoint])

    def test_will_update_observation(self):
        # A user has observation data
        payload = [{
            'precipitation': 1,
            'pressure': 2,
            'wind_gust': 3,
            'wind_speed': 4,
            'wind_direction': 'SSW',
            'wind_degrees': 1,
            'temperature': 6,
            'datetime': format_datetime(delta()),
        }]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(self.live_server_url + self.endpoint, payload)

        # The user submits modified data to the endpoint
        payload[0]['wind_gust'] = 5
        self.assertSubmitPayload(self.live_server_url + self.endpoint, payload, 200)

        # The user queries for the recent record
        base_url = self.live_server_url + self.endpoint
        recent_url = "{0}/recent".format(base_url)
        data = self.assertRecordJSONExists(recent_url)

        # A single record exists
        self.assertEqual(1, len(data))

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])
