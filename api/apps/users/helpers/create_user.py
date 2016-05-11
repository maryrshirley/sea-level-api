from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def create_user(username, email='', *args, **kwargs):
    is_internal_collector = kwargs.pop('is_internal_collector', None)
    available_locations = kwargs.pop('available_locations', [])

    user = User.objects.create(username=username, email=email, *args, **kwargs)
    profile = user.user_profile

    if is_internal_collector is not None:
        profile.is_internal_collector = is_internal_collector

    for location in available_locations:
        profile.available_locations.add(location)

    profile.save()

    Token.objects.create(user=user)  # Create an auth token for the user
    return user


def get_or_create_user(username, *args, **kwargs):
    if User.objects.filter(username=username).exists():
        return User.objects.get(username=username)
    return create_user(username, *args, **kwargs)
