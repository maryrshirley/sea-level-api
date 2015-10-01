import logging

from api.apps.locations.models import Location

LOG = logging.getLogger(__name__)


def get_location_queryset(user):
    """
    Return a QuerySet of Locations that a particular User (including an
    anonymous one) is allowed to view.
    """
    LOG.debug('get_location_queryset({})'.format(repr(user)))

    if user.is_anonymous():
        return get_queryset_anonymous()

    elif user.user_profile.is_internal_collector:
        return get_queryset_collector()

    else:
        return get_queryset_user(user)


def user_can_see_location(user, location):
    """
    Return True if the given User is allowed to view the given Location.
    """
    locations_for_this_user = get_location_queryset(user)
    return locations_for_this_user.filter(id=location.id).exists()


def get_queryset_anonymous():
    return Location.objects.filter(visible=True)


def get_queryset_collector():
    return Location.objects.all()


def get_queryset_user(user):
    return user.user_profile.available_locations
