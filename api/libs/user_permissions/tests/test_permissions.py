import collections

from nose.tools import assert_equal

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from ..permissions_classes import AllowUserSpecificAccess

from .create_test_users_locations import create_test_users_locations


PermissionsTestCase = collections.namedtuple(
    'PermissionsTestCase',
    ','.join([
        'expected_has_permission',
        'expected_has_object_permission',
        'username',
        'location',
        'write_request']))


class UsersLocationsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.users_and_locations = create_test_users_locations()

    @classmethod
    def tearDownClass(cls):
        for obj in cls.users_and_locations.values():
            obj.delete()

    @classmethod
    def _assert_permissions(cls, permissions_class, case):
        if case.username is None:
            user = None
        else:
            user = cls.users_and_locations[case.username]

        request = cls._make_request(case.write_request, user)

        permissions_ob = permissions_class()

        got_has_permission = permissions_ob.has_permission(request, None)

        assert_equal(
            case.expected_has_permission,
            got_has_permission
        )

        if not got_has_permission:
            # If has_permission returned False, we shouldn't call
            # has_object_permission as that isn't how DRF works.
            return

        assert_equal(
            case.expected_has_object_permission,
            permissions_ob.has_object_permission(
                request, None, cls.users_and_locations[case.location])
        )

    @classmethod
    def _make_request(cls, write_request, user):
        factory = RequestFactory()
        if write_request:
            request = factory.post('/')
        else:
            request = factory.get('/')

        request.user = user if user is not None else AnonymousUser()
        # force_authenticate(request, user=user)

        return request


class TestAnonymousUserPermissions(UsersLocationsTestCase):

    def test_can_read_public_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username=None,
            location='location-public-1',
            write_request=False))

    def test_cannot_read_private_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=False,
            username=None,
            location='location-private-1',
            write_request=False))

    def test_cannot_write_public_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,
            expected_has_object_permission=False,
            username=None,
            location='location-public-1',
            write_request=True))

    def test_cannot_write_private_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,
            expected_has_object_permission=False,
            username=None,
            location='location-private-1',
            write_request=True))


class TestLoggedInUserPermissions(UsersLocationsTestCase):

    def test_cannot_read_public_location(self):
        # Strange as it might sound, if the logged in user does not have the
        # public location in their available locations, is isn't available
        # to them. This is to prevent eg Southampton users seeing public
        # Liverpool locations they aren't interested in.
        # By mirroring the behaviour of the /locations/ endpoint it's much
        # simpler to comprehend which locations one has access to.

        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=False,
            username='user-1',
            location='location-public-1',
            write_request=False))

    def test_can_read_private_location_1(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,  # generic read should be allowed
            expected_has_object_permission=True,
            username='user-1',
            location='location-private-1',
            write_request=False))

    def test_cannot_read_private_location_2(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,  # generic read should be allowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-private-2',
            write_request=False))

    def test_cannot_write_public_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,  # generic write disallowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-public-1',
            write_request=True))

    def test_cannot_write_private_location_1(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,  # generic write disallowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-private-1',
            write_request=True))

    def test_cannot_write_private_location_2(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,  # generic write disallowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-private-2',
            write_request=True))


class TestInternalCollectorUserPermissions(UsersLocationsTestCase):

    def test_can_read_public_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-public-1',
            write_request=False))

    def test_can_read_private_location_1(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-private-1',
            write_request=False))

    def test_can_write_public_location(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-public-1',
            write_request=True))

    def test_can_write_private_location_1(self):
        self._assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-private-1',
            write_request=True))
