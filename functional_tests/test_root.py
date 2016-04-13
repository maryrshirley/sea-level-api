import requests

from .base import FunctionalTest


class RootTest(FunctionalTest):

    endpoint = '/1/'

    def test_root_has_links(self):
        fixture_links = [u'locations/', u'predictions/tide-levels/',
                         u'predictions/tide-windows/', u'predictions/weather/',
                         u'sea-levels/']

        root_url = self.live_server_url + self.endpoint

        # The user queries the root of the API
        response = requests.get(root_url)
        self.assertEqual(200, response.status_code)

        # JSON data is returned from the API
        data = response.json()

        # The JSON data contains a links element
        links = [link['href'][len(root_url):]
                 for link in data['links']]

        # The fixutres matches the response
        self.assertEqual(fixture_links, links)

        # Each link exists
        for link in links:
            # Obtain the endpoint
            response = requests.get(root_url + link,
                                    headers=self.authentication_headers)

            # The response is JSON
            data = response.json()

            if response.status_code in [400, 404]:
                self.assertIn('detail', data.keys())
            else:
                self.assertEqual(200, response.status_code)
