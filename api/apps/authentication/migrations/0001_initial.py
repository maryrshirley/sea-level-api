# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginCodeExpired',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('datetime', models.DateTimeField()),
                ('status', models.CharField(max_length=10, choices=[('success', 'Success')])),
                ('code', models.CharField(unique=True, max_length=20, editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+', editable=False)),
            ],
        ),
    ]
