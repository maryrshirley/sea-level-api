import json

from django.core.exceptions import ValidationError
from django.test import TestCase

from nose_parameterized import parameterized
from nose.tools import assert_equal

from nopassword.models import LoginCode

from api.apps.users.helpers import create_user


_URL_AUTH = '/1/authenticate/'
_URL_VALIDATE = _URL_AUTH + 'validate'
_URL_AUTH_EMAIL = _URL_AUTH + 'email'


def load_endpoint_test_cases():
    cases = [(_URL_AUTH, 'POST, OPTIONS',),
             (_URL_VALIDATE, 'POST, OPTIONS',),
             (_URL_AUTH_EMAIL, 'POST, OPTIONS',),
             ]

    return cases


class TestAuthentication(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = create_user('sampleuser')
        self.user.email = 'peter@sealevelresearch.com'
        self.user.save()

    def tearDown(self):
        self.user.delete()
        super(TestCase, self).tearDown()

    @parameterized.expand(load_endpoint_test_cases)
    def test_that_http_options_allowed(self, url, allow):
        response = self.client.options(url)
        assert_equal(200, response.status_code)
        assert_equal(allow, response['Allow'])

    def postAuthEmail(self, email, status_code):
        data = json.dumps({'email': email})
        response = self.client.post(_URL_AUTH_EMAIL, data=data,
                                    content_type='application/json')
        self.assertEqual(status_code, response.status_code)

        return response

    def test_that_email_creates_request(self):
        response = self.postAuthEmail(self.user.email, 201)
        self.assertEquals('OK', response.content)

        self.assertEqual(1, LoginCode.objects.count())

    def test_that_unknownemail_has_error(self):
        response = self.postAuthEmail('bademail@sealevelresearch.com', 400)
        self.assertEquals(['Invalid email bademail@sealevelresearch.com'],
                          response.data['email'])

        self.assertEquals(0, LoginCode.objects.count())

    def test_that_bademail_has_error(self):
        response = self.postAuthEmail('foo', 400)
        self.assertEquals(['Enter a valid email address.'],
                          response.data['email'])

        self.assertEquals(0, LoginCode.objects.count())

    def test_that_noemail_has_error(self):
        data = json.dumps({})
        response = self.client.post(_URL_AUTH_EMAIL, data=data,
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEquals(['This field is required.'],
                          response.data['email'])

        self.assertEquals(0, LoginCode.objects.count())

    def test_that_email_unique(self):
        user2 = create_user('sampleuser2')
        with self.assertRaises(ValidationError) as ex:
            user2.email = self.user.email
            user2.save()
        msg = "Email {0} is already used".format(user2.email)
        self.assertEquals(msg, ex.exception.message)
        user2.delete()
