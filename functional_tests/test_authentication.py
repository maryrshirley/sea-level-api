import re

from django.core import mail
from django.contrib.auth.hashers import make_password

import requests

from .base import FunctionalTest


class AuthenticationTest(FunctionalTest):

    endpoint_auth = '/1/authenticate/'
    endpoint_validate = '/1/authenticate/validate'
    endpoint_email = '/1/authenticate/email'
    endpoint_sms = '/1/authenticate/sms'

    def setUp(self):
        super(AuthenticationTest, self).setUp()
        self.user.password = make_password('test')
        self.user.email = 'test@sealevelresearch.com'
        self.user.save()
        self.auth = {'username': self.user.username, 'password': 'test'}

        self.url_auth = self.live_server_url + self.endpoint_auth
        self.url_validate = self.live_server_url + self.endpoint_validate
        self.url_email = self.live_server_url + self.endpoint_email
        self.url_sms = self.live_server_url + self.endpoint_sms

    def postAuthenticate(self, payload, status_code=200):
        # The user passes authenticate credentials
        response = requests.post(self.url_auth, json=payload)
        self.assertEqual(status_code, response.status_code)

        # The user receives a JSON response
        return response.json()

    def postToken(self, token, status_code=200):
        response = requests.post(self.url_validate, json={'token': token})
        self.assertEqual(status_code, response.status_code)
        return response

    def test_user_authenticates(self):
        # The user authenticates
        payload = self.postAuthenticate(self.auth)

        # The JSON contains a token
        self.assertEqual(1, len(payload))
        token = payload['token']

        # The user is authenticated
        self.postToken(token)

    def test_invalid_user_errors(self):
        # The user passes incorrect authenticate credentials
        auth = {'username': self.user.username, 'password': 'foo'}
        self.postAuthenticate(auth, 400)

    def test_invalid_token_errors(self):
        # The user passes an incorrect token
        payload = {'token': 'foo'}
        self.postToken(payload, 400)

    def test_email_token(self):
        # The user makes a request for an email token
        payload = {'email': self.user.email}
        response = requests.post(self.url_email, json=payload)

        self.assertEqual(201, response.status_code)

        # The email is sent by Django
        self.assertEqual(1, len(mail.outbox))

        # The email body contains a url
        body = mail.outbox[0].body
        url = re.search("(?P<url>https?://[^\s]+).$", body).group('url')

        self.assertRegexpMatches(
            url, self.live_server_url + '/1/authenticate/code/[^\s]+/$')

        # Accessing the URL
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn('token', response.data)
        self.assertIn('email', response.data)

        # The user attempts to send the same token again
        response = self.client.get(url)
        self.assertEqual(410, response.status_code)
        self.assertEqual("Link expired", response.content.decode())

    def test_email_token_post(self):
        # The user makes a request for an email token
        payload = {'email': self.user.email}
        response = requests.post(self.url_email, json=payload)

        self.assertEqual(201, response.status_code)

        # The email is sent by Django
        self.assertEqual(1, len(mail.outbox))

        # The email body contains a url
        body = mail.outbox[0].body
        code = re.search('https?://.+code/(?P<code>.+)/.+$', body) \
            .group('code')
        payload = {'code': code}

        url = self.live_server_url + '/1/authenticate/code/'

        # Accessing the URL
        response = requests.post(url, json=payload)
        self.assertEqual(200, response.status_code)
        self.assertIn('token', response.json())
        self.assertIn('email', response.json())

        # The user attempts to send the same token again
        response = requests.post(url, json=payload)
        self.assertEqual(410, response.status_code)
        self.assertEquals("Link expired", response.content.decode())
