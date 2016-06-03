from nose_parameterized import parameterized

from api.libs.test_utils.base import APIUnitTestCase
from api.libs.test_utils.sea_level import SeaLevelMixin


class TestSeaLevelWindows(APIUnitTestCase, SeaLevelMixin):

    OPTIONS_TESTCASES = [
        ('windows_range_endpoint', 'GET, HEAD, OPTIONS'),
        ('windows_now_endpoint', 'GET, HEAD, OPTIONS'),
    ]

    def setUp(self):
        super(TestSeaLevelWindows, self).setUp()
        self.setUpSeaLevelRequirements()

    def tearDown(self):
        self.tearDownSeaLevelRequirements()
        super(TestSeaLevelWindows, self).tearDown()

    @parameterized.expand(OPTIONS_TESTCASES)
    def test_endpoint_OPTIONS_allowed(self, url, allow):
        url = self.get_url(url)
        self.assert_endpoint_OPTIONS_allowed(url, allow)

    def test_edge_cases(self):
        pass

    def test_authentication(self):
        pass
