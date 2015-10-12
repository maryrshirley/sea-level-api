
from django.contrib.auth.models import User

from api.apps.locations.models import Location


def create_test_users_locations():

    test_objects = {
        'location-public-1': Location.objects.create(
            slug='location-public-1',
            name='location-public-1',
            visible=True),

        'location-private-1': Location.objects.create(
            slug='location-private-1',
            name='location-private-1',
            visible=False),

        'location-private-2': Location.objects.create(
            slug='location-private-2',
            name='location-private-2',
            visible=False),

        'user-1': User.objects.create(
            username='user-1'),

        'user-collector': User.objects.create(
            username='user-collector'),
    }

    user_1_profile = test_objects['user-1'].user_profile
    user_1_profile.available_locations.add(
        test_objects['location-private-1'])
    user_1_profile.save()

    user_collector_profile = test_objects['user-collector'].user_profile
    user_collector_profile.is_internal_collector = True
    user_collector_profile.save()
    return test_objects
