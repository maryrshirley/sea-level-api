from os import environ
import json

import django
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from rest_framework.authtoken.models import Token

from api.libs.test_utils.location import LocationMixin
from api.apps.users.helpers import create_user


class FunctionalTest(StaticLiveServerTestCase, LocationMixin):

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.user = create_user('permitted', is_internal_collector=True)

    def tearDown(self):
        self.user.delete()
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


class SeleniumTest(StaticLiveServerTestCase):

    DEFAULT_WAIT = 5

    def setUp(self):
        binary_path = environ.get('FIREFOX', None)
        binary = FirefoxBinary(binary_path)
        self.browser = webdriver.Firefox(firefox_binary=binary)
        self.browser.implicitly_wait(self.DEFAULT_WAIT)
        super(SeleniumTest, self).setUp()

    def tearDown(self):
        self.browser.quit()
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

    def load_model_page(self, slug, label):
        # User clicks on the admin page
        admin_page = self.browser.find_element_by_class_name('model-' + slug) \
            .find_element_by_link_text(label)
        admin_page.click()

    def add_record(self, slug, label, record):
        self.load_model_page(slug, label)

        # User notices the addlink button
        addlink = self.browser.find_element_by_class_name('addlink')

        text = "Add " + slug
        self.assertEquals(text.upper() if django.VERSION[1] > 8 else text,
                          addlink.text)

        # User clicks on the add button
        addlink.click()

        # User fills in the fields
        for field in record:
            form_field = self.browser.find_element_by_id("id_" + field)
            form_field.send_keys(record[field])

        # User clicks save
        save_button = self.browser.find_element_by_name('_save')
        save_button.click()

    def check_records(self, records):
        # User notices the data table
        tbody = self.browser.find_element_by_tag_name('tbody')

        # User notices the table rows
        tr = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(len(records), len(tr))
