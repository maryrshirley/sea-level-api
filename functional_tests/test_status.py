from collections import OrderedDict

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver


class StatusTest(StaticLiveServerTestCase):

    endpoint = '/1/_status/'

    fixture_links = {
        '/1/_status/surge-predictions/': 'Check Surge predictions',
        '/1/_status/tide-predictions/': 'Check Tide Predictions',
        '/1/_status/weather-predictions/': 'Check Weather Predictions',
        '/1/_status/weather-observations/': 'Check Weather Observations',
        '/1/_status/schedule/': 'Check Schedules',
    }

    def setUp(self):
        super(StatusTest, self).setUp()
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
        super(StatusTest, self).tearDown()

    def replace_live_url(self, url):
        return url.replace(self.live_server_url, '')

    def parse_hrefs(self, elements):
        return OrderedDict(
            {self.replace_live_url(element.get_attribute('href')):
                element.text for element in elements}
        )

    def test_has_sublinks(self):
        # User visits the status page
        self.browser.get(self.live_server_url + self.endpoint)

        # User notices titles within links
        xpath = ".//h2/a"
        sublinks = self.browser.find_elements_by_xpath(xpath)
        hrefs = self.parse_hrefs(sublinks)
        self.assertEqual(set(self.fixture_links), set(hrefs))
