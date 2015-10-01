import logging

from rest_framework import permissions

from .get_location_queryset import user_can_see_location
from .is_read_request import is_read_request

LOG = logging.getLogger(__name__)


class AllowAnonymousReadPublicLocations(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow anonymous users (not logged in) to perform read-only requests.
        Don't allow logged-in users to do anything as they aren't our
        responsibility.
        """
        return is_read_request(request) and request.user.is_anonymous()

    def has_object_permission(self, request, view, location):
        """
        Allow the (anonymous) user to access whatever locations they are
        allowed to access.

        In order for this to be called, `has_permission` must have already
        returned True, so in theory, no need to check `is_read_request` again.
        However it's easier to test if we just check it again :)
        """
        return (is_read_request(request) and
                user_can_see_location(request.user, location))


class AllowInternalCollectorsReadAndWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        If the requesting user is an internal collector, allow them to do
        anything (read & write).

        If the user is not logged in (AnonymousUser) or not an internal
        collector, don't let them do anything - that's not our responsibility.
        """
        if request.user.is_anonymous():
            return False

        return request.user.user_profile.is_internal_collector

    def has_object_permission(self, request, view, location):
        """
        Return the same as `has_permission` as internal collectors have access
        to *all* locations, so we don't do any object-based discrimination.
        """
        return self.has_permission(request, view)


class AllowLoggedInReadTheirLocations(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow logged-in users to perform read-only requests.
        """
        return is_read_request(request) and not request.user.is_anonymous()

    def has_object_permission(self, request, view, location):
        """
        Allow the logged-in user to access whatever locations they are
        allowed to access.

        In order for this to be called, `has_permission` must have already
        returned True, so in theory, no need to check `is_read_request` again.
        However it's easier to test if we just check it again :)
        """
        return (is_read_request(request) and
                user_can_see_location(request.user, location))


class ComposedPermissionsOr(permissions.BasePermission):
    """
    Allow access if any of PERMISSION_CLASSES returns True, eg compose them
    using OR logic.
    """

    def __init__(self, *args, **kwargs):
        super(ComposedPermissionsOr, self).__init__(*args, **kwargs)

        self.permissions_instances = set(
            [cls() for cls in self.PERMISSION_CLASSES])

    def has_permission(self, request, view):
        for instance in self.permissions_instances:
            if instance.has_permission(request, view):
                return True
        return False

    def has_object_permission(self, request, view, obj):
        for instance in self.permissions_instances:
            if instance.has_object_permission(request, view, obj) is True:
                LOG.debug(
                    '{}.has_object_permission({}, {}, {}) returned '
                    'True'.format(repr(instance), repr(request.user), view,
                                  repr(obj)))
                return True
        return False


class AllowUserSpecificAccess(ComposedPermissionsOr):
    PERMISSION_CLASSES = set([
        AllowAnonymousReadPublicLocations,
        AllowLoggedInReadTheirLocations,
        AllowInternalCollectorsReadAndWrite,
    ])
