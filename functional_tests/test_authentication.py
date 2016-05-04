from django.contrib.auth.hashers import make_password

import requests

from .base import FunctionalTest


class AuthenticationTest(FunctionalTest):

    endpoint_auth = '/1/authenticate'
    endpoint_validate = '/1/authenticate/validate'

    def setUp(self):
        super(AuthenticationTest, self).setUp()
        self.user.password = make_password('test')
        self.user.save()
        self.auth = {'username': self.user.username, 'password': 'test'}

        self.url_auth = self.live_server_url + self.endpoint_auth
        self.url_validate = self.live_server_url + self.endpoint_validate

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
