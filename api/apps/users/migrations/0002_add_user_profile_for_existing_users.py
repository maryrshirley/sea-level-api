# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import logging
LOG = logging.getLogger(__name__)


def add_user_profile_for_existing_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('users', 'UserProfile')

    for user in User.objects.all():
        try:
            user.user_profile
        except UserProfile.DoesNotExist:
            LOG.info('Adding user profile to user `{}`'.format(user.username))
            new_user_profile = UserProfile(user=user)
            new_user_profile.save()
        else:
            LOG.info('{} already has user profile'.format(user.username))


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_user_profile_for_existing_users),
    ]
