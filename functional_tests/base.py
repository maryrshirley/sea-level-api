from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import requests

from rest_framework.authtoken.models import Token

from api.apps.locations.models import Location
from api.apps.users.helpers import create_user


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.liverpool = Location.objects.create(
            slug='liverpool', name='Liverpool')
        self.user = create_user('permitted', is_internal_collector=True)

    def tearDown(self):
        self.user.delete()
        self.liverpool.delete()
        super(FunctionalTest, self).tearDown()

    @property
    def token(self):
        return Token.objects.get(user=self.user)

    @property
    def authentication_headers(self):
        return {'Authorization': 'Token {}'.format(self.token)}

    def assertPayloadValueMatches(self, key, json, payload):
        # The key exists in the json
        self.assertIn(key, json[0])
        value = json[0][key]
        self.assertEqual(value, payload[0][key])

    def assertSubmitPayload(self, url, payload):
        response = requests.post(url, json=payload,
                                 headers=self.authentication_headers)

        # The user receives a valid CREATE response
        self.assertEqual(201, response.status_code)

    def assertRecordJSONExists(self, url):
        response = requests.get(url, headers=self.authentication_headers)

        # The user receives a valid OK response
        self.assertEqual(200, response.status_code)

        # The response is JSON
        return response.json()

    def assertPayloadMatchesData(self, data, payload):
        for field, value in payload.items():
            self.assertIn(field, data)
            self.assertEqual(value, data[field])
