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

USERS_AND_LOCATIONS = None


def setUpModule():
    global USERS_AND_LOCATIONS

    USERS_AND_LOCATIONS = create_test_users_locations()


def tearDownModule():
    global USERS_AND_LOCATIONS
    for obj in USERS_AND_LOCATIONS.values():
        obj.delete()


class TestAnonymousUserPermissions(TestCase):

    def test_can_read_public_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username=None,
            location='location-public-1',
            write_request=False))

    def test_cannot_read_private_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=False,
            username=None,
            location='location-private-1',
            write_request=False))

    def test_cannot_write_public_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,
            expected_has_object_permission=False,
            username=None,
            location='location-public-1',
            write_request=True))

    def test_cannot_write_private_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,
            expected_has_object_permission=False,
            username=None,
            location='location-private-1',
            write_request=True))


class TestLoggedInUserPermissions(TestCase):

    def test_cannot_read_public_location(self):
        # Strange as it might sound, if the logged in user does not have the
        # public location in their available locations, is isn't available
        # to them. This is to prevent eg Southampton users seeing public
        # Liverpool locations they aren't interested in.
        # By mirroring the behaviour of the /locations/ endpoint it's much
        # simpler to comprehend which locations one has access to.

        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=False,
            username='user-1',
            location='location-public-1',
            write_request=False))

    def test_can_read_private_location_1(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,  # generic read should be allowed
            expected_has_object_permission=True,
            username='user-1',
            location='location-private-1',
            write_request=False))

    def test_cannot_read_private_location_2(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,  # generic read should be allowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-private-2',
            write_request=False))

    def test_cannot_write_public_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,  # generic write disallowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-public-1',
            write_request=True))

    def test_cannot_write_private_location_1(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,  # generic write disallowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-private-1',
            write_request=True))

    def test_cannot_write_private_location_2(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=False,  # generic write disallowed
            expected_has_object_permission=False,
            username='user-1',
            location='location-private-2',
            write_request=True))


class TestInternalCollectorUserPermissions(TestCase):

    def test_can_read_public_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-public-1',
            write_request=False))

    def test_can_read_private_location_1(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-private-1',
            write_request=False))

    def test_can_write_public_location(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-public-1',
            write_request=True))

    def test_can_write_private_location_1(self):
        _assert_permissions(AllowUserSpecificAccess, PermissionsTestCase(
            expected_has_permission=True,
            expected_has_object_permission=True,
            username='user-collector',
            location='location-private-1',
            write_request=True))


def _assert_permissions(permissions_class, case):
    if case.username is None:
        user = None
    else:
        user = USERS_AND_LOCATIONS[case.username]

    request = _make_request(case.write_request, user)

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
            request, None, USERS_AND_LOCATIONS[case.location])
    )


def _make_request(write_request, user):
    factory = RequestFactory()
    if write_request:
        request = factory.post('/')
    else:
        request = factory.get('/')

    request.user = user if user is not None else AnonymousUser()
    # force_authenticate(request, user=user)

    return request
