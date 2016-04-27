from .base import FunctionalTest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver

from api.libs.test_utils.datetime_utils import delta
from api.libs.view_helpers import format_datetime
from api.libs.test_utils.weather import (CreateObservationMixin, OBSERVATION_B,
                                         OBSERVATION_C, encode_datetime)

DEFAULT_WAIT = 5


class ObservationWeatherBrowser(StaticLiveServerTestCase):

    endpoint = '/1/observations/weather/'

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
        self.assertEquals("Weather Observations", page_header.text)

        # User notices the page description
        xpath = ".//div[@id='content']/div[@class='content-main']/div/p"
        page_desc = self.browser.find_element_by_xpath(xpath)

        # THe page description matches the expected value
        expected = 'Get weather observations. Valid parameters are start and'\
                   ' end (in format 2014-05-01T00:17:00Z)'
        self.assertEquals(expected, page_desc.text)


class ObservationWeatherTest(FunctionalTest, CreateObservationMixin):

    endpoint = '/1/observations/weather/liverpool'

    def test_can_save_observation(self):
        # A user has observation data
        payload = [encode_datetime(self.payload_observation_now())]

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
        endpoints = [key for key in payload[0].keys()
                     if key not in ['datetime', 'supplier']]

        # The user queries each endpoint
        for endpoint in endpoints:
            url = "{0}/{1}/recent".format(base_url, endpoint.replace('_', '-'))

            # The user receives a JSON response from the endpoint
            data = self.assertRecordJSONExists(url)

            # The JSON response contains the observation data
            self.assertIn(endpoint, data[0])
            self.assertEqual(payload[0][endpoint], data[0][endpoint])

            url = "{0}/{1}/latest".format(base_url, endpoint.replace('_', '-'))

            # The user receives a JSON response from the endpoint latest
            data = self.assertRecordJSONExists(url)

            # The JSON response contains the datetime
            # The JSON response contains the observation data
            self.assertIn(endpoint, data[0])
            self.assertEqual(payload[0][endpoint], data[0][endpoint])
            self.assertIn('datetime', data[0])
            self.assertEquals(payload[0]['datetime'], data[0]['datetime'])
            self.assertEqual(payload[0]['datetime'], data[0]['datetime'])

        # The user queries the latest endpoint
        latest_url = "{0}/latest".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

    def test_observation_date_order(self):
        url = self.live_server_url + self.endpoint

        # A user has observation data
        payload = [
            encode_datetime(self.payload_observation(datetime=delta(hours=-4)))
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(url, payload)

        payload_2 = [
            encode_datetime(self.payload_observation(OBSERVATION_B,
                                                     datetime=delta(hours=-2)))
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(url, payload_2)

        # The user queries for the recent record
        base_url = self.live_server_url + self.endpoint
        recent_url = "{0}/recent".format(base_url)
        data = self.assertRecordJSONExists(recent_url)

        # The first data matches the second payload
        self.assertPayloadMatchesData(data[0], payload_2[0])

        # The second data matches the first payload
        self.assertPayloadMatchesData(data[1], payload[0])

    def test_observation_latest(self):
        base_url = self.live_server_url + self.endpoint

        # A user has observation data
        payload = [
            encode_datetime(self.payload_observation(datetime=delta(hours=-4)))
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        payload_2 = [
            encode_datetime(self.payload_observation(OBSERVATION_B,
                                                     datetime=delta(hours=-6)))
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload_2)

        # The user queries the latest endpoint
        latest_url = "{0}/latest".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # A single record is returned
        self.assertEqual(1, len(data))

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

    def test_will_update_observation(self):
        # A user has observation data
        payload = [encode_datetime(self.payload_observation_now())]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(self.live_server_url + self.endpoint, payload)

        # The user submits modified data to the endpoint
        payload[0]['wind_gust'] = 5
        self.assertSubmitPayload(self.live_server_url + self.endpoint, payload,
                                 200)

        # The user queries for the recent record
        base_url = self.live_server_url + self.endpoint
        recent_url = "{0}/recent".format(base_url)
        data = self.assertRecordJSONExists(recent_url)

        # A single record exists
        self.assertEqual(1, len(data))

        # The user data matches the original  payload
        self.assertPayloadMatchesData(data[0], payload[0])

    def test_fields_are_optional(self):
        # A user has partial observation data
        payload = [encode_datetime(
            self.payload_observation_now(OBSERVATION_C))]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(self.live_server_url + self.endpoint, payload)

        # The user queries for the recent record
        base_url = self.live_server_url + self.endpoint
        recent_url = "{0}/recent".format(base_url)
        data = self.assertRecordJSONExists(recent_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])
