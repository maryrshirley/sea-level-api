from .base import FunctionalTest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver

from api.libs.test_utils.datetime_utils import delta
from api.libs.view_helpers import format_datetime

DEFAULT_WAIT = 5


class PredictionWeatherBrowser(StaticLiveServerTestCase):

    endpoint = '/1/predictions/weather/'

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)

    def tearDown(self):
        self.browser.quit()

    def test_has_documentation(self):
        # User visits the weather api
        self.browser.get(self.live_server_url + self.endpoint)

        # User notices the page-header
        page_header = self.browser.find_element_by_class_name('page-header')

        # The page header matches the expected value
        self.assertEquals("Weather Predictions", page_header.text)


class PredictionWeatherTest(FunctionalTest):

    endpoint = '/1/predictions/weather/liverpool'

    def test_can_save_forecast(self):
        # A user has forecast data
        payload = [{
            'precipitation': 1,
            'pressure': 2,
            'wind_gust': 3,
            'wind_speed': 4,
            'wind_direction': 'N',
            'wind_degrees': 6,
            'temperature': 7,
            'supplier': 'met_office',
            'valid_from': format_datetime(delta()),
            'valid_to': format_datetime(delta(hours=2)),
        }]

        base_url = self.live_server_url + self.endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        latest_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

        # The user queries for a range record
        range_url = '{0}?start={1}&end={2}' \
            .format(base_url, format_datetime(delta()),
                    format_datetime(delta(hours=2)))
        data = self.assertRecordJSONExists(range_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

        # The user can has individual endpoints to query
        endpoints = [key for key in payload[0].keys() if key not in
                     ['datetime', 'supplier', 'valid_from', 'valid_to']]

        # The user queries each endpoint
        for endpoint in endpoints:
            url = "{0}/{1}/now".format(base_url, endpoint.replace('_', '-'))

            # The user receives a JSON response from the endpoint
            data = self.assertRecordJSONExists(url)

            # The JSON response contains the observation data
            self.assertIn(endpoint, data[0])
            self.assertEqual(payload[0][endpoint], data[0][endpoint])

    def test_can_save_multiple_forecasts(self):
        # A user has multiple forecase data
        payload = [
            {
                'precipitation': 10,
                'pressure': 11,
                'wind_gust': 12,
                'wind_speed': 13,
                'wind_direction': 'S',
                'wind_degrees': 15,
                'temperature': 16,
                'supplier': 'met_office',
                'valid_from': '2016-04-26T06:00:00Z',
                'valid_to': '2016-04-26T12:00:00Z',
            },
            {
                'precipitation': 10,
                'pressure': 11,
                'wind_gust': 12,
                'wind_speed': 13,
                'wind_direction': 'S',
                'wind_degrees': 15,
                'temperature': 16,
                'supplier': 'met_office',
                'valid_from': '2016-04-26T12:00:00Z',
                'valid_to': '2016-04-26T18:00:00Z',
            },
        ]

        base_url = self.live_server_url + self.endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        latest_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # The user data matches the original payload
        for index, elem in enumerate(data):
            self.assertPayloadMatchesData(data[index], payload[index])

        # The user queries for a range record
        range_url = '{0}?start=2016-04-26T06:00:00Z&end=2016-04-26T18:00:00Z' \
            .format(base_url)
        data = self.assertRecordJSONExists(range_url)

        # The user data matches the original payload
        for index, elem in enumerate(data):
            self.assertPayloadMatchesData(data[index], payload[index])

    def test_forecast_date_order(self):
        base_url = self.live_server_url + self.endpoint

        # A user has forecast data
        payload = [
            {
                'precipitation': 10,
                'pressure': 11,
                'wind_gust': 12,
                'wind_speed': 13,
                'wind_direction': 'S',
                'wind_degrees': 15,
                'temperature': 16,
                'supplier': 'met_office',
                'valid_from': format_datetime(delta(hours=4)),
                'valid_to': format_datetime(delta(hours=6)),
            }
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # A user has previous forecast data
        payload_2 = [
            {
                'precipitation': 20,
                'pressure': 21,
                'wind_gust': 22,
                'wind_speed': 23,
                'wind_direction': 'S',
                'wind_degrees': 15,
                'temperature': 26,
                'supplier': 'met_office',
                'valid_from': format_datetime(delta(hours=2)),
                'valid_to': format_datetime(delta(hours=4)),
            }
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload_2)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        latest_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # record-0 matches the second payload
        self.assertPayloadMatchesData(data[0], payload_2[0])

        # record-1 matches the first payload
        self.assertPayloadMatchesData(data[1], payload[0])

    def test_will_update_forecast(self):
        # A user has forecast data
        payload = [
            {
                'precipitation': 10,
                'pressure': 11,
                'wind_gust': 12,
                'wind_speed': 13,
                'wind_direction': 'S',
                'wind_degrees': 15,
                'temperature': 16,
                'supplier': 'met_office',
                'valid_from': format_datetime(delta()),
                'valid_to': format_datetime(delta(hours=2)),
            }
        ]

        base_url = self.live_server_url + self.endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user submits the data to the endpoint again
        payload[0]['pressure'] = 12
        self.assertSubmitPayload(base_url, payload, 200)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        latest_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # A single record exists
        self.assertEqual(1, len(data))

        # The user data matches the second payload
        for index, elem in enumerate(data):
            self.assertPayloadMatchesData(data[index], payload[index])
