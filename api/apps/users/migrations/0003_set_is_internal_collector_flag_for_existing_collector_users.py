# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_is_internal_collector_flags(apps, schema_editor):
    UserProfile = apps.get_model('users', 'UserProfile')

    for user_profile in UserProfile.objects.all():
        print(user_profile.user.username)
        if user_profile.user.username.endswith('-collector'):
            user_profile.is_internal_collector = True
            user_profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_user_profile_for_existing_users'),
    ]

    operations = [
        migrations.RunPython(set_is_internal_collector_flags),
    ]
