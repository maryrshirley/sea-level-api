# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0003_add_location_visible_to_location_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('is_internal_collector', models.BooleanField(default=False, help_text='Select to treat this user as a collector or other "superuser" software written internally. This will grant the user read and write access to most of the API endpoints, so beware.')),
                ('available_locations', models.ManyToManyField(to='locations.Location', help_text="Select which Locations the user has read access to. This affects which Locations are returned by the /locations/ endpoint as well as the user's ability to access data through other endpoints such as tide-levels.<br>Note that this has no effect on collector users as these can access all Locations.", related_name='user_profiles')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='user_profile')),
            ],
        ),
    ]
