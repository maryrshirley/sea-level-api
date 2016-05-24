# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='arrival_sea_level',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='departure_sea_level',
            field=models.FloatField(null=True),
        ),
    ]
