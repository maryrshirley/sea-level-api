from .base import FunctionalTest, SeleniumTest
from .base_weather import WeatherAdminTest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import formats

from selenium import webdriver

from api.libs.test_utils.datetime_utils import delta
from api.libs.test_utils.mixins import LocationMixin
from api.libs.test_utils.weather import CreatePredictionMixin, encode_datetime
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

        # User notices the page description
        xpath = ".//div[@id='content']/div[@class='content-main']/div/p"
        page_desc = self.browser.find_element_by_xpath(xpath)

        # THe page description matches the expected value
        expected = 'Get weather predictions. Valid parameters are start and'\
                   ' end (in format 2014-05-01T00:17:00Z)'
        self.assertEquals(expected, page_desc.text)


class PredictionAdmin(WeatherAdminTest):

    def test_prediction_admin(self):
        predictions = [
            self.create_prediction(valid_from=delta(hours=-4),
                                   valid_to=delta(hours=-2)),
            self.create_prediction_now()
        ]

        super(PredictionAdmin, self)._test_admin(predictions, 'predictions',
                                                 self.assert_valid_dates)

        for prediction in predictions:
            prediction.delete()

    def assert_valid_dates(self, row, obj):
        from_field = row.find_element_by_class_name('field-valid_from')
        valid_from = formats.date_format(obj.valid_from,
                                         "DATETIME_FORMAT")
        self.assertEqual(valid_from, from_field.text)


class PredictionWeatherStatus(SeleniumTest, CreatePredictionMixin,
                              LocationMixin):

    endpoint = '/1/_status/weather-predictions/'

    def setUp(self):
        super(PredictionWeatherStatus, self).setUp()
        self.setUpLocation()

    def tearDown(self):
        self.tearDownLocation()
        super(PredictionWeatherStatus, self).tearDown()

    def test_location_has_status(self):
        # A prediction exists
        prediction = self.create_prediction_now()

        # User visits the status page
        self.browser.get(self.live_server_url + self.endpoint)

        # User notices header
        page_header = self.browser \
            .find_element_by_xpath(".//div[@class='page-header']/h1")
        self.assertEquals('Weather Predictions: OK', page_header.text)

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

        # User notices a single table row
        tr = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(1, len(tr))

        # User notices two table elements
        td = tr[0].find_elements_by_tag_name('td')
        self .assertEqual(2, len(td))

        # User notices the location name matches
        self.assertEquals("Liverpool", td[0].text)

        # User notices the status is OK
        self.assertEquals("OK", td[1].text)

        prediction.delete()


class PredictionWeatherTest(FunctionalTest, CreatePredictionMixin):

    endpoint = '/1/predictions/weather/liverpool'

    def test_can_save_forecast(self):
        # A user has forecast data
        payload = [encode_datetime(self.payload_prediction_now())]

        base_url = self.live_server_url + self.endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        now_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(now_url)

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

            url = "{0}/{1}/latest".format(base_url, endpoint.replace('_', '-'))

            # The user receives a JSON response from the endpoint latest
            data = self.assertRecordJSONExists(url)

            # The JSON response contains valid dates
            # The JSON response contains the observation data
            self.assertIn(endpoint, data[0])
            self.assertEqual(payload[0][endpoint], data[0][endpoint])
            self.assertIn('valid_from', data[0])
            self.assertEquals(payload[0]['valid_from'], data[0]['valid_from'])
            self.assertEqual(payload[0]['valid_from'], data[0]['valid_from'])
            self.assertIn('valid_to', data[0])
            self.assertEquals(payload[0]['valid_to'], data[0]['valid_to'])
            self.assertEqual(payload[0]['valid_to'], data[0]['valid_to'])

        # The user queries the latest endpoint
        latest_url = "{0}/latest".format(base_url)
        data = self.assertRecordJSONExists(latest_url)

        # The user data matches the original payload
        self.assertPayloadMatchesData(data[0], payload[0])

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
                'weather_type': 'sunny_day',
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
                'weather_type': 'fog',
                'valid_from': '2016-04-26T12:00:00Z',
                'valid_to': '2016-04-26T18:00:00Z',
            },
        ]

        base_url = self.live_server_url + self.endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        now_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(now_url)

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

    def test_multiple_day_range_forecasts(self):
        base_url = self.live_server_url + self.endpoint

        # A user has forecast data
        payload = [
            encode_datetime(self.payload_prediction(
                valid_from=delta(hours=2),
                valid_to=delta(hours=4)
            )),
            encode_datetime(self.payload_prediction(
                True,
                valid_from=delta(days=1, hours=2),
                valid_to=delta(days=1, hours=4)
            ))
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user queries for a range record
        base_url = self.live_server_url + self.endpoint
        range_url = "{0}?start={1}&end={2}" \
            .format(base_url, format_datetime(delta()),
                    format_datetime(delta(days=2)))
        data = self.assertRecordJSONExists(range_url)

        self.assertEqual(2, len(data))

    def test_forecast_date_order(self):
        base_url = self.live_server_url + self.endpoint

        # A user has forecast data
        payload = [encode_datetime(self.payload_prediction(
            valid_from=delta(hours=4),
            valid_to=delta(hours=6)
        ))]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # A user has previous forecast data
        payload_2 = [encode_datetime(self.payload_prediction(
            True,
            valid_from=delta(hours=2),
            valid_to=delta(hours=4)
        ))]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload_2)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        now_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(now_url)

        # record-0 matches the second payload
        self.assertPayloadMatchesData(data[0], payload_2[0])

        # record-1 matches the first payload
        self.assertPayloadMatchesData(data[1], payload[0])

    def test_prediction_latest(self):
        base_url = self.live_server_url + self.endpoint

        # A user has forecast data
        payload = [
            encode_datetime(self.payload_prediction(valid_from=delta(hours=2),
                                                    valid_to=delta(hours=4)))
        ]

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # A user has forecast data
        payload_2 = [
            encode_datetime(self.payload_prediction(True,
                                                    valid_from=delta(hours=4),
                                                    valid_to=delta(hours=6)))
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

    def test_will_update_forecast(self):
        # A user has forecast data
        payload = [encode_datetime(self.payload_prediction_now())]

        base_url = self.live_server_url + self.endpoint

        # The user submits the data to the endpoint
        self.assertSubmitPayload(base_url, payload)

        # The user submits the data to the endpoint again
        payload[0]['pressure'] = 12
        self.assertSubmitPayload(base_url, payload, 200)

        # The user queries for the latest record
        base_url = self.live_server_url + self.endpoint
        now_url = "{0}/now".format(base_url)
        data = self.assertRecordJSONExists(now_url)

        # A single record exists
        self.assertEqual(1, len(data))

        # The user data matches the second payload
        for index, elem in enumerate(data):
            self.assertPayloadMatchesData(data[index], payload[index])
