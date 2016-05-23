from api.apps.locations.models import Location
from api.apps.users.helpers import create_user


def create_test_users_locations():

    test_objects = {
        'location-public-1': Location.objects.create(
            slug='location-public-1',
            name='location-public-1',
            min_depth=1.0,
            under_keal=2.0,
            visible=True),

        'location-private-1': Location.objects.create(
            slug='location-private-1',
            name='location-private-1',
            min_depth=1.0,
            under_keal=2.0,
            visible=False),

        'location-private-2': Location.objects.create(
            slug='location-private-2',
            name='location-private-2',
            min_depth=1.0,
            under_keal=2.0,
            visible=False),
    }

    test_objects['user-1'] = create_user(
        'user-1',
        available_locations=[test_objects['location-private-1']]
    )

    test_objects['user-collector'] = create_user(
        'user-collector',
        is_internal_collector=True
    )

    return test_objects
