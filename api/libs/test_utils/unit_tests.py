from nose.tools import assert_equal

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.apps.locations.models import Location
from api.apps.users.helpers import create_user
from api.libs.test_utils import decode_json

from .mixins import PostJsonMixin


class ViewAuthenticationTest(APITestCase, PostJsonMixin):
    @classmethod
    def setUpClass(cls, url, good_data):
        super(ViewAuthenticationTest, cls).setUpClass()

        cls.url = url
        cls.liverpool = Location.objects.create(
            slug='liverpool', name='Liverpool')

        cls.permitted = create_user('permitted', is_internal_collector=True)
        cls.forbidden = create_user('forbidden', is_internal_collector=False)

        cls.good_data = good_data

    @classmethod
    def tearDownClass(cls):
        super(ViewAuthenticationTest, cls).tearDownClass()

        cls.permitted.delete()
        cls.forbidden.delete()
        cls.liverpool.delete()

    def _test_that_no_authentication_header_returns_http_401(self):
        # 401 vs 403: http://stackoverflow.com/a/6937030
        response = self._post_json(self.url, [])
        assert_equal(401, response.status_code)

    def _test_that_user_without_add___permission_gets_403(self):
        token = Token.objects.get(user__username='forbidden').key
        response = self._post_json(
            self.url,
            [self.good_data],
            HTTP_AUTHORIZATION='Token {}'.format(token))
        assert_equal(403, response.status_code)
        assert_equal(
            {'detail': 'You do not have permission to perform this action.'},
            decode_json(response.content))

    def _test_that_user_with_add__permission_can_post(self):
        token = Token.objects.get(user__username='permitted').key
        response = self._post_json(
            self.url,
            [self.good_data],
            HTTP_AUTHORIZATION='Token {}'.format(token))
        assert_equal(201, response.status_code)
