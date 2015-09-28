from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from api.apps.locations.models import Location


class UserProfile(models.Model):
    class Meta:
        app_label = 'users'

    user = models.OneToOneField(User, related_name='user_profile')

    is_internal_collector = models.BooleanField(
        default=False,
        help_text=('Select to treat this user as a collector or other '
                   '"superuser" software written internally. This will grant '
                   'the user read and write access to most of the API '
                   'endpoints, so beware.'))

    available_locations = models.ManyToManyField(
        Location,
        related_name='user_profiles',
        help_text=('Select which Locations the user has read access to. This '
                   'affects which Locations are returned by the /locations/ '
                   'endpoint as well as the user\'s ability to access data '
                   'through other endpoints such as tide-levels.<br>Note '
                   'that this has no effect on collector users as these '
                   'can access all Locations.'))


def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        up = UserProfile(user=user)
        up.save()

post_save.connect(create_profile, sender=User)
