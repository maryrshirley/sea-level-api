import logging

from api.apps.locations.models import Location

LOG = logging.getLogger(__name__)


def get_queryset(user):
    LOG.info('get_queryset({})'.format(repr(user)))

    if user.is_anonymous():
        return get_queryset_anonymous()

    elif user.user_profile.is_internal_collector:
        return get_queryset_collector()

    else:
        return get_queryset_user(user)


def get_queryset_anonymous():
    return Location.objects.filter(visible=True)


def get_queryset_collector():
    return Location.objects.all()


def get_queryset_user(user):
    return user.user_profile.available_locations
