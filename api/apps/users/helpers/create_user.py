from django.contrib.auth.models import User


def create_user(username, *args, **kwargs):
    is_internal_collector = kwargs.pop('is_internal_collector', None)
    available_locations = kwargs.pop('available_locations', [])

    user = User.objects.create(username=username, *args, **kwargs)
    profile = user.user_profile

    if is_internal_collector is not None:
        profile.is_internal_collector = is_internal_collector

    for location in available_locations:
        profile.available_locations.add(location)

    profile.save()
    return user
