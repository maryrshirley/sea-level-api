import json

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from rest_framework.authtoken.models import Token

from api.apps.locations.models import Location
from api.apps.users.helpers import create_user
from api.libs.test_utils.mixins import LocationMixin


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

    def assertSubmitPayload(self, url, payload, status_code=201):
        response = requests.post(url, json=payload,
                                 headers=self.authentication_headers)

        # The user receives a valid CREATE response
        self.assertEqual(status_code, response.status_code)

        # The user receives a confirmation payload
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(payload), len(data))

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


class SeleniumTest(StaticLiveServerTestCase, LocationMixin):

    DEFAULT_WAIT = 5

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(self.DEFAULT_WAIT)
        self.setUpLocation()
        super(SeleniumTest, self).setUp()

    def tearDown(self):
        self.browser.quit()
        self.tearDownLocation()
        super(SeleniumTest, self).tearDown()


class AdminTest(object):

    def setUpAdmin(self):
        self.admin = User.objects.create_superuser('admin',
                                                   'admin@example.com',
                                                   'admin')
        self.admin_url = self.live_server_url + '/admin/'

    def tearDownAdmin(self):
        self.admin.delete()

    def loginAdmin(self):
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)

    def loadAdmin(self):
        self.browser.get(self.admin_url)
        self.loginAdmin()
